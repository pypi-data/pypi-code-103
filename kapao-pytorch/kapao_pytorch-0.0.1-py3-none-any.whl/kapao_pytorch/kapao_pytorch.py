import sys
from pathlib import Path

FILE = Path(__file__).absolute()
sys.path.append(FILE.parents[0].as_posix())  # add kapao/ to path

import argparse
import os.path as osp

import cv2
import imageio
import numpy as np
import torch
import yaml
from models.experimental import attempt_load
from pytube import YouTube
from tqdm import tqdm
from utils.augmentations import letterbox
from utils.datasets import LoadImages
#from val import run_nms, post_process_batch
from utils.general import (check_dataset, check_file, check_img_size, colorstr,
                           non_max_suppression_kp, scale_coords, set_logging)
from utils.torch_utils import select_device, time_sync

# youtube id, stream tag, start time, end time
# shuffle: yBZ0Y2t0ceo, 135, 34, 42
# flash mob: 2DiQUX11YaY, 136, 188, 196
# red light green light: nrchfeybHmw, 135, 56, 72

PAD_COLOR = (114 / 255, 114 / 255, 114 / 255)
TAG_RES = {135: '480p', 136: '720p', 137: '1080p'}

class kapao_pytorch:
	def __init__(self):
		pass

	def run_nms(self,data, model_out):
		if data['iou_thres'] == data['iou_thres_kp'] and data['conf_thres_kp'] >= data['conf_thres']:
			# Combined NMS saves ~0.2 ms / image
			dets = non_max_suppression_kp(model_out, data['conf_thres'], data['iou_thres'], num_coords=data['num_coords'])
			person_dets = [d[d[:, 5] == 0] for d in dets]
			kp_dets = [d[d[:, 4] >= data['conf_thres_kp']] for d in dets]
			kp_dets = [d[d[:, 5] > 0] for d in kp_dets]
		else:
			person_dets = non_max_suppression_kp(model_out, data['conf_thres'], data['iou_thres'],
												 classes=[0],
												 num_coords=data['num_coords'])

			kp_dets = non_max_suppression_kp(model_out, data['conf_thres_kp'], data['iou_thres_kp'],
											 classes=list(range(1, 1 + len(data['kp_flip']))),
											 num_coords=data['num_coords'])
		return person_dets, kp_dets


	def post_process_batch(self,data, imgs, paths, shapes, person_dets, kp_dets,
						   two_stage=False, pad=0, device='cpu', model=None, origins=None):

		batch_bboxes, batch_poses, batch_scores, batch_ids = [], [], [], []
		n_fused = np.zeros(data['num_coords'] // 2)

		if origins is None:  # used only for two-stage inference so set to 0 if None
			origins = [np.array([0, 0, 0]) for _ in range(len(person_dets))]

		# process each image in batch
		for si, (pd, kpd, origin) in enumerate(zip(person_dets, kp_dets, origins)):
			nd = pd.shape[0]
			nkp = kpd.shape[0]

			if nd:
				path, shape = Path(paths[si]) if len(paths) else '', shapes[si][0]
				img_id = int(osp.splitext(osp.split(path)[-1])[0]) if path else si

				# TWO-STAGE INFERENCE (EXPERIMENTAL)
				if two_stage:
					gs = max(int(model.stride.max()), 32)  # grid size (max stride)
					crops, origins, crop_shapes = [], [], []

					for bbox in pd[:, :4].cpu().numpy():
						x1, y1, x2, y2 = map(int, map(round, bbox))
						x1, x2 = max(x1, 0), min(x2, data['imgsz'])
						y1, y2 = max(y1, 0), min(y2, data['imgsz'])
						h0, w0 = y2 - y1, x2 - x1
						crop_shapes.append([(h0, w0)])
						crop = np.transpose(imgs[si][:, y1:y2, x1:x2].cpu().numpy(), (1, 2, 0))
						crop = cv2.copyMakeBorder(crop, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=PAD_COLOR)  # add padding
						h0 += 2 * pad
						w0 += 2 * pad
						origins = [np.array([x1 - pad, y1 - pad, 0])]
						crop_pre = letterbox(crop, data['imgsz'], color=PAD_COLOR, stride=gs, auto=False)[0]
						crop_input = torch.Tensor(np.transpose(np.expand_dims(crop_pre, axis=0), (0, 3, 1, 2))).to(device)

						out = model(crop_input, augment=True, kp_flip=data['kp_flip'], scales=data['scales'], flips=data['flips'])[0]
						person_dets, kp_dets = run_nms(data, out)
						_, poses, scores, img_ids, _ = post_process_batch(
							data, crop_input, paths, [[(h0, w0)]], person_dets, kp_dets, device=device, origins=origins)

						# map back to original image
						if len(poses):
							poses = np.stack(poses, axis=0)
							poses = poses[:, :, :2].reshape(poses.shape[0], -1)
							poses = scale_coords(imgs[si].shape[1:], poses, shape)
							poses = poses.reshape(poses.shape[0], data['num_coords'] // 2, 2)
							poses = np.concatenate((poses, np.zeros((poses.shape[0], data['num_coords'] // 2, 1))), axis=-1)
						poses = [p for p in poses]  # convert back to list

				# SINGLE-STAGE INFERENCE
				else:
					scores = pd[:, 4].cpu().numpy()  # person detection score
					bboxes = scale_coords(imgs[si].shape[1:], pd[:, :4], shape).round().cpu().numpy()
					poses = scale_coords(imgs[si].shape[1:], pd[:, -data['num_coords']:], shape).cpu().numpy()
					poses = poses.reshape((nd, -data['num_coords'], 2))
					poses = np.concatenate((poses, np.zeros((nd, poses.shape[1], 1))), axis=-1)

					if data['use_kp_dets'] and nkp:
						mask = scores > data['conf_thres_kp_person']
						poses_mask = poses[mask]

						if len(poses_mask):
							kpd[:, :4] = scale_coords(imgs[si].shape[1:], kpd[:, :4], shape)
							kpd = kpd[:, :6].cpu()

							for x1, y1, x2, y2, conf, cls in kpd:
								x, y = np.mean((x1, x2)), np.mean((y1, y2))
								pose_kps = poses_mask[:, int(cls - 1)]
								dist = np.linalg.norm(pose_kps[:, :2] - np.array([[x, y]]), axis=-1)
								kp_match = np.argmin(dist)
								if conf > pose_kps[kp_match, 2] and dist[kp_match] < data['overwrite_tol']:
									pose_kps[kp_match] = [x, y, conf]
									n_fused[int(cls - 1)] += 1
							poses[mask] = poses_mask

					poses = [p + origin for p in poses]

				batch_bboxes.extend(bboxes)
				batch_poses.extend(poses)
				batch_scores.extend(scores)
				batch_ids.extend([img_id] * len(scores))

		return batch_bboxes, batch_poses, batch_scores, batch_ids, n_fused



	def load_pretrained_model(self,args):
		device = select_device(args.device, batch_size=1)
		print('Using device: {}'.format(device))

		with open(str(FILE.parents[0]) + '/' + args.data) as f:
			data = yaml.safe_load(f)  # load data dict

		# add inference settings to data dict
		data['imgsz'] = args.imgsz
		data['conf_thres'] = args.conf_thres
		data['iou_thres'] = args.iou_thres
		data['use_kp_dets'] = not args.no_kp_dets
		data['conf_thres_kp'] = args.conf_thres_kp
		data['iou_thres_kp'] = args.iou_thres_kp
		data['conf_thres_kp_person'] = args.conf_thres_kp_person
		data['overwrite_tol'] = args.overwrite_tol
		data['scales'] = args.scales
		data['flips'] = [None if f == -1 else f for f in args.flips]
		

		model = attempt_load(args.weights, map_location=device)  # load FP32 model
		stride = int(model.stride.max())  # model stride
		imgsz = check_img_size(args.imgsz, s=stride)  # check image size

		if device.type != 'cpu':
			model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once

		return data,model,stride,imgsz

	def run_inference(self,model,frame,data,stride,imgsz,args):
			im0 = frame.copy()
		
		
			img = letterbox(im0, imgsz, stride=stride, auto=True)[0]
			# Convert
			img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
			img = np.ascontiguousarray(img)

			img = torch.from_numpy(img).to(args.device)
			img = img.float()  # uint8 to fp16/32
			img = img / 255.0  # 0 - 255 to 0.0 - 1.0
			if len(img.shape) == 3:
				img = img[None]  # expand for batch dim
			
			out = model(img, augment=True, kp_flip=data['kp_flip'], scales=data['scales'], flips=data['flips'])[0]
			person_dets, kp_dets = self.run_nms(data, out)
			#import pdb;pdb.set_trace()
			bboxes, poses, _, _, _ = self.post_process_batch(data, img, [], [[im0.shape[:2]]], person_dets, kp_dets)

			# im0[433:455, 626:816] = np.mean(im0[434:454, 626:816], axis=(0, 1))  # remove patch
			im0_copy = im0.copy()

			# DRAW POSES
			for j, (bbox, pose) in enumerate(zip(bboxes, poses)):
				x1, y1, x2, y2 = bbox
				cv2.rectangle(im0_copy, (int(x1), int(y1)), (int(x2), int(y2)), args.color, thickness=1)
				if args.face:
					for x, y, c in pose[data['kp_face']]:
						if not args.kp_obj or c:
							cv2.circle(im0_copy, (int(x), int(y)), args.kp_size, args.color, args.kp_thick)
				for seg in data['segments'].values():
					if not args.kp_obj or (pose[seg[0], -1] and pose[seg[1], -1]):
						pt1 = (int(pose[seg[0], 0]), int(pose[seg[0], 1]))
						pt2 = (int(pose[seg[1], 0]), int(pose[seg[1], 1]))
						cv2.line(im0_copy, pt1, pt2, args.color, args.line_thick)
			im0 = cv2.addWeighted(im0, args.alpha, im0_copy, 1 - args.alpha, gamma=0)

			return im0,bboxes
