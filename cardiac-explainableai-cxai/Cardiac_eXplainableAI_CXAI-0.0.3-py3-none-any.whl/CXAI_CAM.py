from tf_keras_vis.utils import normalize
from tf_keras_vis.gradcam import Gradcam
from matplotlib import cm as mat_cm
from sklearn.metrics import jaccard_score
from tf_keras_vis.gradcam import GradcamPlusPlus
import tensorflow as tf
import numpy as np
import pickle
from . import CXAI_evaluation
import os
import pandas as pd
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt

def insert_vals_in_df(df, values):
    for i, val in zip(range(len(df), len(df)+len(values)), values):
        df.loc[i] = val
    return df

def model_modifier(m):
    m.layers[-1].activation = tf.keras.activations.linear
    return m

def loss_pred(output):
    return (output[0][pat_diag_pred_num])

# def loss_dia(output):
#     return (output[0][patient_diagnosis_num])

def read_pickle_file(path):
    with open(path, 'rb') as file:
        return pickle.load(file)


class CAM_generator(object):
    def __init__(self, _config, _dataloader, modelpath, threshold = 0.5, subsets = ["test", "val", "train"], already_existing = False):
        self.config = _config
        self.th =  [threshold] if isinstance(threshold, (int, float)) else threshold
        self.dataloader = _dataloader
        self.model, self.foldnr = CXAI_evaluation.load_model_for_eval(modelpath)
        
        self.config.data.withmask = True #True so the segmentation masks can be loaded with: self.dataloader.read_h5data()
        _,_,self.mask = self.dataloader.read_h5data()
        self.config.data.withmask = False #False so the labels instead of the segmentation masks are loaded when calling self.dataloader.generate_ds_form_cv_list(numOfPass=self.foldnr)
        train_img,train_label,test_img,test_label,val_img,val_label,temp_idx = self.dataloader.generate_ds_form_cv_list(numOfPass=self.foldnr)
        
        if already_existing:
            self.load_existing_data(subsets)
        else:
            self.generateCAMsforallsubsets(subsets, train_img,train_label,test_img,test_label,val_img,val_label,temp_idx)

    def load_existing_data(self, subsets):
        print("Loading existing data from location", self.config.file.modeldir)
        for curr_subset_name in subsets:
            print("Loading data for subset", curr_subset_name)
            if curr_subset_name == "test":
                self.df_jac_test =          pd.read_csv(os.path.join(self.config.file.modeldir,curr_subset_name+"_jaccard_ch1_df_fold_"+str(self.foldnr)+".csv"), index_col=0)
                self.gt_input_data_test =   read_pickle_file(os.path.join(self.config.file.modeldir,curr_subset_name+"_gt_input_ch1_data_output_fold_"+str(self.foldnr)))
                self.gradCAMs_test =        read_pickle_file(os.path.join(self.config.file.modeldir,curr_subset_name+"_gradCAMs_ch1_output_fold_"+str(self.foldnr)))
            if curr_subset_name == "val":
                self.df_jac_val =           pd.read_csv(os.path.join(self.config.file.modeldir,curr_subset_name+"_jaccard_ch1_df_fold_"+str(self.foldnr)+".csv"), index_col=0)
                self.gt_input_data_val =    read_pickle_file(os.path.join(self.config.file.modeldir,curr_subset_name+"_gt_input_ch1_data_output_fold_"+str(self.foldnr)))
                self.gradCAMs_val =         read_pickle_file(os.path.join(self.config.file.modeldir,curr_subset_name+"_gradCAMs_ch1_output_fold_"+str(self.foldnr)))
            if curr_subset_name == "train":
                self.df_jac_train =         pd.read_csv(os.path.join(self.config.file.modeldir,curr_subset_name+"_jaccard_ch1_df_fold_"+str(self.foldnr)+".csv"), index_col=0)
                self.gt_input_data_train =  read_pickle_file(os.path.join(self.config.file.modeldir,curr_subset_name+"_gt_input_ch1_data_output_fold_"+str(self.foldnr)))
                self.gradCAMs_train =       read_pickle_file(os.path.join(self.config.file.modeldir,curr_subset_name+"_gradCAMs_ch1_output_fold_"+str(self.foldnr)))
        
    def generateCAMsforallsubsets(self, subsets, train_img,train_label,test_img,test_label,val_img,val_label,temp_idx):
        for curr_subset_name in subsets:
            if curr_subset_name == "test":
                self.df_jac_test, self.gt_input_data_test, self.gradCAMs_test = self.GradCAM_generation_subset_only_channel1(subset_name = curr_subset_name, data_imgs = test_img, data_labels = test_label, testmodel = self.model, X_data = self.dataloader.X_test, temp_idx = temp_idx)
            if curr_subset_name == "val":
                self.df_jac_val, self.gt_input_data_val, self.gradCAMs_val = self.GradCAM_generation_subset_only_channel1(subset_name = curr_subset_name, data_imgs = val_img, data_labels = val_label, testmodel = self.model, X_data = self.dataloader.X_valid, temp_idx = temp_idx)
            if curr_subset_name == "train":
                self.df_jac_train, self.gt_input_data_train, self.gradCAMs_train = self.GradCAM_generation_subset_only_channel1(subset_name = curr_subset_name, data_imgs = train_img, data_labels = train_label, testmodel = self.model, X_data = self.dataloader.X_train, temp_idx = temp_idx)
    
    def select_data_from_subset(self, subset_name):
        if (subset_name == "val" ):
            return self.df_jac_val, self.dataloader.X_valid, self.gradCAMs_val, self.gt_input_data_val  
        elif (subset_name == "train" ):
            return self.df_jac_train, self.dataloader.X_train, self.gradCAMs_train, self.gt_input_data_train
        elif (subset_name == "test" ):
            return self.df_jac_test, self.dataloader.X_test, self.gradCAMs_test, self.gt_input_data_test      
    
    def calc_jaccard_score(self, mask,prediction, jaccard_cutoff = 0.5):
        return jaccard_score(self.convert_for_jaccard(mask,th = 1, ismask = True),self.convert_for_jaccard(prediction, th = jaccard_cutoff ,ismask = False), average='binary')

    def convert_for_jaccard(self, data,th = .45, ismask = False):
        if ismask == True:
            th = 1
        else:
            data = data / 255
        img = data.copy()
        img[data >= th] = 1
        img[data < th] = 0
        return img.flatten()

    def calc_jaccard_score_only_channel1(self, gtmask, gradCAMs, current_info):
        cam_values = []
        gradCAMTypes = ['GradCAM','GradCAM++']
        vamVar = ["pred", "pred"]
            
        for i,cam in enumerate(gradCAMs):
            for th in self.th:
                cam_channel_var =  cam[:,:,0]

                cam_values.append([current_info["pat_num"],current_info["assigned_set"],current_info["slice_nr"], #self.foldnr,
                            self.calc_jaccard_score(gtmask, cam_channel_var, th), th ,gradCAMTypes[i],vamVar[i], "1.Channel",
                            current_info["model_prediction"], current_info["GT"], current_info["correct_prediction"], current_info["prediction_scores"],
                            current_info["idx_num_in_set"], current_info["HDF5_img_idx"]])
        return cam_values

    def GradCAM_generation_subset_only_channel1(self, subset_name, data_imgs, data_labels, testmodel, X_data, temp_idx):
        gradCAMs_temp, plt_imgs = [],[]
        gt_input_data, gradCAMs = [],[]

        jac_df = pd.DataFrame(columns=["pat_num","assigned_set","slice_nr",
                                    "jaccard_score", "threshold","GradCAM_type","GradCAM_loss","CAM_variation",
                                    "model_prediction","GT","correct_prediction","prediction_scores",
                                    "idx_num_in_set","HDF5_img_idx"])
        
        data_batches = tf.data.Dataset.from_tensor_slices((data_imgs,data_labels)).batch(self.config.model.batch_size)
        y_pred = testmodel.predict(data_batches)

        y_pred_class = np.argmax(y_pred, axis=1)
        label_class = np.argmax(data_labels, axis=1)

        itercnt = 0
        tmp_cam_save = []
        
        global patient_diagnosis_num
        global pat_diag_pred_num

        for k in tqdm(range(len(temp_idx[subset_name+'_img_idx'])), total = len(temp_idx[subset_name+'_img_idx']), desc= "Generating GradCAMs for "+subset_name+" subset"):
            gradCAMs_temp, plt_imgs = [],[]
            for slice_cnt in range(len(temp_idx[subset_name+'_img_idx'][k])):
                patient_diagnosis_num = label_class[itercnt] 
                pat_diag_pred_num = y_pred_class[itercnt] 
                eval_imgs = data_imgs[itercnt]
                smask = self.mask[temp_idx[subset_name+'_img_idx'][k][slice_cnt]]

                gradcam = Gradcam(testmodel,model_modifier=model_modifier,clone=False)
                cam = gradcam(loss_pred,eval_imgs,penultimate_layer=-1)
                cam = normalize(cam)    
                heatmap_pred = np.uint8(mat_cm.jet(cam[0])[..., :3] * 255)
                
                gradcampp = GradcamPlusPlus(testmodel,model_modifier,clone=False)
                cam = gradcampp(loss_pred,eval_imgs,penultimate_layer=-1)
                cam = normalize(cam)
                heatmap_pp_pred = np.uint8(mat_cm.jet(cam[0])[..., :3] * 255)
                tmp_cam_save = [heatmap_pred,heatmap_pp_pred]
                    
                gradCAMs_temp.append(tmp_cam_save)
                plt_imgs.append([smask,eval_imgs[:,:,0]])

                current_info = {
                    "pat_num": X_data['fold_'+str(self.foldnr)][k],
                    "assigned_set": subset_name,
                    "slice_nr":slice_cnt,
                    "model_prediction":pat_diag_pred_num,
                    "GT": patient_diagnosis_num ,
                    "correct_prediction": (pat_diag_pred_num == patient_diagnosis_num),
                    "prediction_scores": y_pred[itercnt],
                    "idx_num_in_set": itercnt,
                    "HDF5_img_idx": temp_idx[subset_name+'_img_idx'][k][slice_cnt]
                }

                temp_values = self.calc_jaccard_score_only_channel1(smask, tmp_cam_save, current_info)
                jac_df = insert_vals_in_df(jac_df, temp_values)

                itercnt = itercnt + 1

            gt_input_data.append(plt_imgs)
            gradCAMs.append(gradCAMs_temp)

        jac_df.to_csv(os.path.join(self.config.file.modeldir,subset_name+"_jaccard_ch1_df_fold_"+str(self.foldnr)+".csv"))
        
        print("Jaccard Scores saved at path:", str(os.path.join(self.config.file.modeldir,subset_name+"_jaccard_ch1_df_fold_"+str(self.foldnr)+".csv")))

        with open(os.path.join(self.config.file.modeldir,subset_name+"_gradCAMs_ch1_output_fold_"+str(self.foldnr)), 'wb') as fp:
            pickle.dump(gradCAMs, fp)

        with open(os.path.join(self.config.file.modeldir,subset_name+"_gt_input_ch1_data_output_fold_"+str(self.foldnr)), 'wb') as fp: #! actually unnecessary bc already stored in H5 file
            pickle.dump(gt_input_data, fp)
            
        return jac_df, gt_input_data, gradCAMs
    
    
    def plot_it_main(self, subset_name = "test", n = 10,best = "rand", only_unique_patients = True, figuresize = (20, 12)):
        df_selected, X_data_selected, cam_data_selected, input_data_selected = self.select_data_from_subset(subset_name)
          
        temp_df = get_best_or_worst_n_of_df(df_selected, n = n,best = best, only_unique_patients =  only_unique_patients) 
        display(temp_df)
        imgs, scores = self.get_n_pre_selected_CAMs(df = temp_df, X_data_subset = X_data_selected, 
                                    cam_data_subset = cam_data_selected, input_data_subset = input_data_selected)
        self.plot_all_in_subplots(imgs, scores, suptitle = '_'.join((subset_name, "fold" ,str(self.foldnr), "best_selected-" + str(best), str(n), "samples", "only_unique_patients" if only_unique_patients else "not_only_unique_patients") ), hspace = .1, wspace=.1, figsize=figuresize)
        
    def get_n_pre_selected_CAMs(self, df, X_data_subset, cam_data_subset, input_data_subset):
        """
        Get output and scores of the pre selected CAMs (best/worst cases)
        Info:
            in cam_data:
                first index == X_data['fold_'+str(self.foldnr)].index(pat_num)
                second index == slice nr
                third index == which CAM variation --> selected_cam_idx
                [widht][height][channel] ==> due to it being 1.Channel take only ...[:,:,0]
        """
        output, scores = [], []
        for n in range(len(df)):
            selected_case = df.loc[n]
            selected_pat_num = selected_case.pat_num
            selected_pat_num_idx = list(X_data_subset['fold_'+str(self.foldnr)]).index(selected_pat_num) 
            selected_slice_nr = selected_case.slice_nr
            selected_cam_var_types = '_'.join((selected_case.GradCAM_type,selected_case.GradCAM_loss))
            cam_var_types = ['GradCAM_pred','GradCAM++_pred']

            selected_cam_idx = cam_var_types.index(selected_cam_var_types)

            selected_cam = cam_data_subset[selected_pat_num_idx][selected_slice_nr][selected_cam_idx][:,:,0]
            selected_cam_gt = input_data_subset[selected_pat_num_idx][selected_slice_nr][0]
            selected_cam_input_img  = input_data_subset[selected_pat_num_idx][selected_slice_nr][1]

            output.append([selected_cam, selected_cam_gt, selected_cam_input_img])
            scores.append(selected_case.jaccard_score)

        return output, scores

    def plot_all_in_subplots(self, temp_img, scores, dividernum = 2, suptitle="",hspace = .5, wspace=.15, figsize=(25, 20), title_fontsize = 18):
        rowlen = int(len(temp_img)//dividernum + (len(temp_img) % dividernum > 0))
        collen = int(len(temp_img[0])*dividernum)
        numitems = len(temp_img[0])
        fig, axs = plt.subplots(rowlen,collen, figsize=figsize)
        fig.subplots_adjust(hspace = hspace, wspace=wspace)

        axs = axs.ravel()
        cnt = 0
        
        for i in range(numitems * len(temp_img)):
            if(i% numitems == 1): #should be overlay of Input img + genereted CAM
                axs[i].set_title("CMR with generated CAM\n Jaccard score = " + str(round(scores[cnt],3)), fontsize=title_fontsize)
                axs[i].imshow(temp_img[cnt][2], cmap='gray')
                axs[i].imshow(temp_img[cnt][0], cmap='jet', alpha=0.4)
                axs[i].grid(False)
                axs[i].axis('off')
            elif(i % numitems == 2): #should be Input Img + Mask == GT
                axs[i].set_title("CMR with\n ground truth mask", fontsize=title_fontsize)
                axs[i].imshow(temp_img[cnt][2], cmap='gray')
                axs[i].imshow(temp_img[cnt][1], cmap='jet', alpha=0.4)
                axs[i].grid(False)
                axs[i].axis('off')
                cnt = cnt + 1
            elif(i % numitems == 0): 
                axs[i].set_title("CMR slice", fontsize=title_fontsize)
                axs[i].imshow(temp_img[cnt][2], cmap='gray')
                axs[i].grid(False)
                axs[i].axis('off')
                
        if (numitems * len(temp_img) < len(axs)):
            for j in range(i, len(axs)):
                axs[j].axis('off')
                axs[j].grid(None)

        plt.tight_layout()
        plt.savefig(os.path.join(self.config.file.modeldir,"CAM_all_in_one"+ suptitle + ".png"))
        plt.show()

def get_best_or_worst_n_of_df(df, n= 10, th = .5, colmumnname = "jaccard_score" , best = True, only_unique_patients = True):
    if only_unique_patients:
        if best == True:
            df_temp = df[df.threshold == th]
            return df_temp[df_temp[colmumnname] == df_temp.groupby('pat_num')[colmumnname].transform('max')].nlargest(n, colmumnname).reset_index(drop = True)
        elif best == False:
            df_temp = df[df.threshold == th]
            return df_temp[df_temp[colmumnname] == df_temp.groupby('pat_num')[colmumnname].transform('min')].nsmallest(n, colmumnname).reset_index(drop = True)
        else:
            return df.sample(n).reset_index()
    else:
        if best == True:
            return df[df.threshold == th].nlargest(n, colmumnname).reset_index(drop = True)
        elif best == False:
            return df[df.threshold == th].nsmallest(n, colmumnname).reset_index(drop = True)
        else:
            return df.sample(n).reset_index()
        
