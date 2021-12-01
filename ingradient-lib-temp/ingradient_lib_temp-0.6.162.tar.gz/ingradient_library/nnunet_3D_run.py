from ingradient_library.dataloads import *
from ingradient_library.inference import Inference
from ingradient_library.preprocessing import *
from ingradient_library.dataloads import DataLoader3D
from ingradient_library.dataloads import CustomDataset
from ingradient_library.preprocessing import Resampling
from ingradient_library.preprocessing import Normalizer
from ingradient_library.preprocessing import Get_target_spacing
from ingradient_library.transform import Transform
from ingradient_library.get_nnunet_setting import get_transform_params
from ingradient_library.deep_supervision_loss import *
from ingradient_library.trainer import Trainer
from ingradient_library.model import *
from ingradient_library.model import *
from ingradient_library.get_information import get_imbalance_weight
from ingradient_library.optimizer import SAMSGD
from torch.utils.data.dataset import random_split
from ingradient_library.get_information import get_imbalance_weight
from ingradient_library.active_contour_loss import *
import torch.nn.functional as F
import torch.optim as optim
import torch.nn as nn


torch.manual_seed(1)

def nnunet_3D_run(LOAD_PATH, SAVE_MODEL_PATH, GPU_DEVICE_INDEX, patch_size, batch_size, n_classes, n_modalities):
    transform = Transform(*get_transform_params(GPU_DEVICE_INDEX))
    dataset = CustomDataset(LOAD_PATH, normalizer = Normalizer())
    tr_dataset, val_dataset = random_split(dataset, [len(dataset) - len(dataset)//9, len(dataset)//9])
    tr_dataloader = DataLoader3D(tr_dataset, patch_size = patch_size, device = GPU_DEVICE_INDEX, batch_size = batch_size, transform = transform)
    val_dataloader = DataLoader3D(val_dataset, patch_size = patch_size, device = GPU_DEVICE_INDEX, batch_size = batch_size)
    weight = get_imbalance_weight(LOAD_PATH, n_classes)

    model = Deep_Supervision_UNet3d(patch_size = patch_size, n_modalities = n_modalities, final_output_channels = n_classes, is_binary = False).to(GPU_DEVICE_INDEX)
    loss2 = Multi_Dice_Loss(n_classes)
    loss1 = nn.CrossEntropyLoss(reduction = 'none', weight = torch.tensor(weight).float().to(GPU_DEVICE_INDEX))
    optimizer = optim.SGD(model.parameters(), lr = 1e-2, nesterov = True, momentum = 0.99)
    scheduler = optim.lr_scheduler.LambdaLR(optimizer=optimizer,
                                lr_lambda=lambda epoch: 0.95 ** epoch)
    trainer = Trainer(tr_dataloader = tr_dataloader, val_dataloader= val_dataloader, model =  model, optimizer = optimizer, scheduler = scheduler, losses = [loss1, loss2], save_path = SAVE_MODEL_PATH, is_deep_supervision = True)
    trainer.run()



def nnunet_3D_run_narrow(LOAD_PATH, SAVE_MODEL_PATH, GPU_DEVICE_INDEX, patch_size, batch_size, n_classes, n_modalities):
    transform = Transform(*get_transform_params(GPU_DEVICE_INDEX))
    dataset = CustomDataset(LOAD_PATH, normalizer = Normalizer())
    print(dataset[0][0].shape)
    tr_dataset, val_dataset = random_split(dataset, [len(dataset) - len(dataset)//9, len(dataset)//9])
    tr_dataloader = DataLoader3D(tr_dataset, patch_size = patch_size, device = GPU_DEVICE_INDEX, batch_size = batch_size, transform = transform)
    val_dataloader = DataLoader3D(val_dataset, patch_size = patch_size, device = GPU_DEVICE_INDEX, batch_size = batch_size)
    weight = get_imbalance_weight(LOAD_PATH, n_classes)

    model = Deep_Supervision_UNet3d_Narrow(patch_size = patch_size, n_modalities = n_modalities, final_output_channels = n_classes, is_binary = False).to(GPU_DEVICE_INDEX)
    loss2 = Multi_Dice_Loss(n_classes)
    loss1 = nn.CrossEntropyLoss(reduction = 'none', weight = torch.tensor(weight).float().to(GPU_DEVICE_INDEX))
    optimizer = optim.Adam(model.parameters(), lr = 1e-2)
    scheduler = optim.lr_scheduler.LambdaLR(optimizer=optimizer,
                                lr_lambda=lambda epoch: 0.95 ** epoch)
    trainer = Trainer(tr_dataloader = tr_dataloader, val_dataloader= val_dataloader, model =  model, optimizer = optimizer, scheduler = scheduler, losses = [loss1, loss2], save_path = SAVE_MODEL_PATH, is_deep_supervision = True)
    trainer.run()



def narrow_inference_run(LOAD_PATH, MODEL_LOAD_PATH,  SAVE_RESULT_PATH, GPU_DEVICE_INDEX, patch_size, n_classes, n_modalities):
    dataset = CustomDataset(LOAD_PATH, normalizer = Normalizer())
    _, val_dataset = random_split(dataset, [len(dataset) - len(dataset)//9, len(dataset)//9])
    ifr = Inference(dataset = val_dataset, n_classes = n_classes, patch_size = patch_size, device = GPU_DEVICE_INDEX, save_path=SAVE_RESULT_PATH)
    model = Deep_Supervision_UNet3d_Narrow(patch_size = patch_size, n_modalities = n_modalities, final_output_channels = n_classes, is_binary = False).to(GPU_DEVICE_INDEX)
    file = torch.load(MODEL_LOAD_PATH)
    model.load_state_dict(file)
    ifr.run(model, mode='dice')
    print(ifr.get_result())


def nnunet_lung_run(LOAD_PATH, SAVE_MODEL_PATH, GPU_DEVICE_INDEX, patch_size = (208, 208, 112), batch_size = 2, n_classes = 2, n_modalities = 1):
    transform = Transform(*get_transform_params(GPU_DEVICE_INDEX))
    resample = Resampling(target_spacing = (0.79, 0.79, 1.24), anisotropy_axis_index=np.array([]))
    dataset = CustomDataset(LOAD_PATH, normalizer = Fixed_Normalizer(), resample = resample)
    print(dataset[0][0].shape, patch_size)
    tr_dataset, val_dataset = random_split(dataset, [len(dataset) - len(dataset)//9, len(dataset)//9])
    tr_dataloader = DataLoader3D(tr_dataset, patch_size = patch_size, device = GPU_DEVICE_INDEX, batch_size = batch_size, transform = transform)
    val_dataloader = DataLoader3D(val_dataset, patch_size = patch_size, device = GPU_DEVICE_INDEX, batch_size = batch_size)
    model = Deep_Supervision_UNet3d_Lung(patch_size = patch_size, n_modalities = n_modalities, final_output_channels = n_classes, is_binary = False).to(GPU_DEVICE_INDEX)
    optimizer = SAMSGD(model.parameters(), lr = 1e-9, nesterov = True, momentum = 0.99, weight_decay= 0.05)
    
    writer = SummaryWriter()
    current_iter = 0
    val_iter = 0
    criterion1 = FastACELoss3DV2(classes = n_classes).to(GPU_DEVICE_INDEX)
    criterion2 = nn.CrossEntropyLoss(reduction = 'sum', weight = torch.tensor([1,39500]).float().to(GPU_DEVICE_INDEX))
    step = 0
    v_step = 0
    for e in range(1000):
        tr_dataloader.new_epoch()
        n_iter = 0
        model.train()
        epoch_tr_loss = 0
        epoch_tr_div = 0
        epoch_val_loss = 0
        epoch_val_div = 0
        while not tr_dataloader.is_end():
            current_iter += 1
            n_iter += 1
            images, seg = tr_dataloader.generate_train_batch()
            if isinstance(optimizer, SAMSGD):
                def closure():
                    optimizer.zero_grad()
                    output = model(images)
                    output = output.permute(0,2,3,4,1)
                    output = torch.softmax(output, dim = -1)
                    output = output.permute(0,-1,1,2,3)
                    loss1 = criterion1(output, F.one_hot(seg,2).permute(0,-1,1,2,3))
                    loss2 = criterion2(output, seg) / 1e+3
                    writer.add_scalar('Lung/Train/AC Loss', loss1.item(), step)
                    writer.add_scalar('Lung/Train/CE Loss', loss2.item() * 1e+3, step)
                    loss = loss1 + loss2
                    loss.backward()
                    return loss
                optimizer.step(closure)
                epoch_tr_loss = 1
                epoch_tr_div = 1
            step+=1

       
        val_dataloader.new_epoch()
        val_loss = 0
        n_iter = 0
        model.eval()
        while not val_dataloader.is_end():
            val_iter +=1
            n_iter +=1
            with torch.no_grad():
                images, seg = val_dataloader.generate_train_batch()
                output = model(images)
                output = output.permute(0,2,3,4,1)
                output = torch.softmax(output, dim = -1)
                output = output.permute(0,-1,1,2,3)
                loss1 = criterion1(output, F.one_hot(seg,2).permute(0,-1,1,2,3))
                loss2 = criterion2(output, seg) / 1e+3
                writer.add_scalar('Lung/Valid/AC Loss', loss1.item(), step)
                writer.add_scalar('Lung/Valid/CE Loss', loss2.item(), step)
                loss = loss1 + loss2
                epoch_val_loss += loss.item()
                epoch_val_div += 1
            v_step += 1


        writer.add_scalar('epoch\Loss_train', epoch_tr_loss/epoch_tr_div , e)
        writer.add_scalar('epoch\Loss_val', epoch_val_loss/epoch_val_div , e) 

        file_name = 'epoch'+ str(e) + '_model_state_dict.pkl'
        torch.save(model.state_dict(), os.path.join(SAVE_MODEL_PATH, file_name))


def nnunet_brain_run(LOAD_PATH, SAVE_MODEL_PATH, GPU_DEVICE_INDEX, patch_size = (144, 160, 144), batch_size = 2, n_classes = 5, n_modalities = 4):
    transform = Transform(*get_transform_params(GPU_DEVICE_INDEX))
    dataset = CustomDataset(LOAD_PATH, normalizer = Normalizer())
    print(dataset[0][0].shape, patch_size)
    tr_dataset, val_dataset = random_split(dataset, [len(dataset) - len(dataset)//9, len(dataset)//9])
    tr_dataloader = DataLoader3D(tr_dataset, patch_size = patch_size, device = GPU_DEVICE_INDEX, batch_size = batch_size, transform = transform)
    val_dataloader = DataLoader3D(val_dataset, patch_size = patch_size, device = GPU_DEVICE_INDEX, batch_size = batch_size)
    weight = get_imbalance_weight(LOAD_PATH, n_classes)

    model = Deep_Supervision_UNet3d(patch_size = patch_size, n_modalities = n_modalities, final_output_channels = n_classes, is_binary = False).to(GPU_DEVICE_INDEX)
    loss2 = Multi_Dice_Loss(n_classes)
    loss1 = nn.CrossEntropyLoss(reduction = 'none', weight = torch.tensor(weight).float().to(GPU_DEVICE_INDEX))
    optimizer = optim.Adam(model.parameters(), lr = 1e-2)
    scheduler = optim.lr_scheduler.LambdaLR(optimizer=optimizer,
                                lr_lambda=lambda epoch: 0.95 ** epoch)
    trainer = Trainer(tr_dataloader = tr_dataloader, val_dataloader= val_dataloader, model =  model, optimizer = optimizer, scheduler = scheduler, losses = [loss1, loss2], save_path = SAVE_MODEL_PATH, is_deep_supervision = True)
    trainer.run()
