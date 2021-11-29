import torch_geometric
from torch_geometric.datasets import TUDataset
import torch
from genagg.AggGNN import patch_conv_with_aggr
from genagg import GenAggSparse
from torch_geometric.datasets import Planetoid, Reddit, CoraFull, Amazon, KarateClub, GNNBenchmarkDataset, ZINC
from torch_geometric.loader import DataLoader
from torch_geometric.nn import global_add_pool

from torch.utils.tensorboard import SummaryWriter
import random
import functools


mean_losses = {}
mean_hparam = {}
seeds = range(3)


def get_loss_fn(task):
    if task == 'graph_class':
        return torch.nn.functional.cross_entropy
    elif task == 'node_class':
        return torch.nn.functional.cross_entropy
    elif task == 'graph_regr':
        return torch.nn.functional.mse_loss

def build_gnn(
        layer, 
        task='node_class', 
        num_hidden_layers=2, 
        hidden_size=32,
        track_params=False,
        **layer_kwargs):
    hidden_layers = []
    tracked_params = []
    for i in range(num_hidden_layers):
        hidden_layers.append((layer(hidden_size, hidden_size, **layer_kwargs), "x, e -> x"))
        hidden_layers.append((torch.nn.ReLU(), 'x -> x'))

    core = [
        (torch.nn.Linear(gnn_in, hidden_size), 'x -> x'),
        *hidden_layers,
    ]
    # Output layers
    if task == 'node_class':
        core += [
            (torch.nn.Linear(hidden_size, gnn_out), 'x -> x'),
            # Log softmax is in cross_entropy
        ]
    elif task == 'graph_class':
        core += [
            (global_add_pool, 'x, b, size -> x'),
            (torch.nn.Linear(hidden_size, hidden_size), 'x -> x'),
            (torch.nn.ReLU(), 'x -> x'),
            (torch.nn.Linear(hidden_size, hidden_size), 'x -> x'),
            (torch.nn.ReLU(), 'x -> x'),
            (torch.nn.Linear(hidden_size, gnn_out), 'x -> x'),
        ]
    elif task == 'graph_regr':
        core += [
            (global_add_pool, 'x, b, size -> x'),
            (torch.nn.Linear(hidden_size, hidden_size), 'x -> x'),
            (torch.nn.ReLU(), 'x -> x'),
            (torch.nn.Linear(hidden_size, hidden_size), 'x -> x'),
            (torch.nn.ReLU(), 'x -> x'),
            (torch.nn.Linear(hidden_size, 1), 'x -> x'),
            #(torch.nn.Flatten(), 'x -> x')
        ]
    else:
        raise NotImplementedError()
        

    
    model = torch_geometric.nn.Sequential(
        "x, e, b, size",
        core
    ).to(device)

    model.name = f'{layer.__name__}_{num_hidden_layers}x{hidden_size}'

    if track_params:
        mods = [m[0] for m in core if hasattr(m[0], 'aggr')]
        params = {}
        for i, m in enumerate(mods):
            params[f'p_{i}'] = m.aggr.p
            params[f'a_{i}'] = m.aggr.a
        model.tracked_params = params
    hparams = {
        'hidden_size': hidden_size,
        'task': task,
        'hidden_layers': num_hidden_layers,
        'layer_type': layer.__name__, 
    }
    return model, hparams


for dataset, dset_name, dset_type in [
    #(GNNBenchmarkDataset(root='/tmp/gbd', name='CLUSTER'), 'CLUSTER', 'node_class'), 
    #(GNNBenchmarkDataset(root='/tmp/gbd', name='PATTERN'), 'PATTERN', 'node_class'),
    #(GNNBenchmarkDataset(root='/tmp/gbd', name='CSL'), 'CSL', 'graph_class'),
    #(Planetoid(root='/tmp/cora', name='Cora'), 'CORA', 'node_class'),
    #(GNNBenchmarkDataset(root='/tmp/gbd', name='CIFAR10'), 'CIFAR10', 'graph_class'),
    #(GNNBenchmarkDataset(root='/tmp/gbd', name='MNIST'), 'MNIST', 'graph_class'),
    #(ZINC(root='/tmp/zinc', subset=True), 'ZINC', 'graph_regr')
    ]:

    loss_fn = get_loss_fn(dset_type)
    

    for seed in seeds:
        torch.manual_seed(seed)
        random.seed(seed)
        train_samples = 0
        train_batches = 0
        gnns = {}
        hparams = {}

        #dataset = TUDataset(root='/tmp/MUTAG', name='MUTAG', use_node_attr=True)
        # dataset = GNNBenchmarkDataset(root='/tmp/gbd', name=dset_name)
        loader = DataLoader(dataset, batch_size=64, shuffle=True)
        gnn_in = dataset.num_node_features
        gnn_out = dataset.num_classes
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Reduce domain cuz some datasets have big inputs
        gc_layer = torch_geometric.nn.GraphConv
        rggc_layer = torch_geometric.nn.ResGatedGraphConv
        gcn_layer = torch_geometric.nn.GCNConv
        gc_agg = patch_conv_with_aggr(gc_layer, GenAggSparse, p_domain=[-1.95, 1.95])
        rggc_agg = patch_conv_with_aggr(rggc_layer, GenAggSparse, p_domain=[-1.95, 1.95])
        gcn_agg = patch_conv_with_aggr(gcn_layer, GenAggSparse, p_domain=[-1.95, 1.95])


        gnns["gc/2x32/mean"], hparams["gc/2x32/mean"] = build_gnn(gc_layer, aggr='add', task=dset_type)
        gnns["gc/2x32/sum"], hparams["gc/2x32/sum"] = build_gnn(gc_layer, aggr='mean', task=dset_type)
        gnns["gc/2x32/max"], hparams["gc/2x32/max"] = build_gnn(gc_layer, aggr='max', task=dset_type)
        gnns["gc/2x32/genagg"], hparams["gc/2x32/genagg"] = build_gnn(gc_agg, track_params=True, task=dset_type) 

        gnns["rggc/2x32/mean"], hparams["rggc/2x32/mean"] = build_gnn(rggc_layer, aggr='add', task=dset_type)
        gnns["rggc/2x32/sum"], hparams["rggc/2x32/sum"] = build_gnn(rggc_layer, aggr='mean', task=dset_type)
        gnns["rggc/2x32/max"], hparams["rggc/2x32/max"] = build_gnn(rggc_layer, aggr='max', task=dset_type)
        gnns["rggc/2x32/genagg"], hparams["rggc/2x32/genagg"] = build_gnn(rggc_agg, track_params=True, task=dset_type) 

        gnns["gcn/2x32/mean"], hparams["gcn/2x32/mean"] = build_gnn(gcn_layer, aggr='add', task=dset_type)
        gnns["gcn/2x32/sum"], hparams["gcn/2x32/sum"] = build_gnn(gcn_layer, aggr='mean', task=dset_type)
        gnns["gcn/2x32/max"], hparams["gcn/2x32/max"] = build_gnn(gcn_layer, aggr='max', task=dset_type)
        gnns["gcn/2x32/genagg"], hparams["gcn/2x32/genagg"] = build_gnn(gcn_agg, track_params=True, task=dset_type) 

        '''
        gnns["2x64/mean"], hparams["2x64/mean"] = build_gnn(base_layer, hidden_size=64, aggr='add', task=dset_type)
        gnns["2x64/sum"], hparams["2x64/sum"] = build_gnn(base_layer, hidden_size=64, aggr='mean', task=dset_type)
        gnns["2x64/max"], hparams["2x64/max"] = build_gnn(base_layer, hidden_size=64, aggr='max', task=dset_type)
        gnns["2x64/genagg"], hparams["2x64/genagg"] = build_gnn(agg_layer, hidden_size=64, track_params=True, task=dset_type) 

        gnns["3x32/mean"], hparams["3x32/mean"] = build_gnn(base_layer, num_hidden_layers=3, aggr='add', task=dset_type)
        gnns["3x32/sum"], hparams["3x32/sum"] = build_gnn(base_layer, num_hidden_layers=3, aggr='mean', task=dset_type)
        gnns["3x32/max"], hparams["3x32/max"] = build_gnn(base_layer, num_hidden_layers=3, aggr='max', task=dset_type)
        gnns["3x32/genagg"], hparams["3x32/genagg"] = build_gnn(agg_layer, num_hidden_layers=3, track_params=True, task=dset_type) 
        '''
        
        writers = {}
        mean_writers = {}
        for k in gnns:
            writers[k] = SummaryWriter(log_dir=f'runs/{dset_name}/{k}-{seed}') 
            mean_writers[k] = SummaryWriter(log_dir=f'runs/{dset_name}/{k}-overall') 

        params = []
        for gnn in gnns.values():
            params += list(gnn.parameters())

        opt = torch.optim.Adam(params, lr=0.01, weight_decay=5e-4)

        for epoch in range(20):
            total_losses = {}
            min_loss = {}
            for data in loader:
                if data.x.dtype != torch.float:
                    data.x = data.x.float()
                data = data.to(device)
                opt.zero_grad()
                losses = torch.tensor([0], device=device)
                loss = {}
                for name, gnn in gnns.items():
                    out = gnn(data.x, data.edge_index, data.batch, data.num_graphs)
                    # Loss for reporting
                    loss[name] = loss_fn(out, data.y)
                    writers[name].add_scalar(f'train/{dset_name}/loss', loss[name], train_batches)
                    # Loss for backprop
                    losses = losses + loss[name]

                    # Mean loss over all trials
                    mean_losses[train_batches] = mean_losses.get(train_batches, {})
                    mean_losses[train_batches][name] = mean_losses[train_batches].get(name, 0) + loss[name]
                    min_loss[name] = min(
                        min_loss.get(name, 1e5), float(loss[name]) 
                    )
                    # Log p,a
                    if hasattr(gnns[name], 'tracked_params'):
                        for k, v in gnns[name].tracked_params.items():
                            writers[name].add_scalar(
                                f'train/{dset_name}/{k}', float(v.detach()), train_batches
                            )
                    
                train_batches += 1
                losses.backward()
                opt.step()
                train_samples += data.num_graphs

            print(f"Seed {seed} Epoch {epoch} Batches Processed {train_batches}")

        for name, writer in writers.items():
            writer.add_hparams(
                {"dataset": dset_name, "seed": seed, **hparams[name]},
                {"hparam/min_train_loss": min_loss[name]},
                # Merge runs so we don't create a ton of files
                run_name="."
            )

    for train_batches, d in mean_losses.items():
        for name, loss in d.items():
            loss = loss / len(seeds)
            mean_writers[name].add_scalar(f'train/{dset_name}/loss', loss, train_batches)

        for w in writers.values():
            w.flush()

    for w in mean_writers.values():
        w.flush()
