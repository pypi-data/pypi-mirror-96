# from __future__ import annotations
import json
import os
import sys
import timeit
from datetime import datetime
from functools import partial
from shutil import Error
from sys import exit as x
from typing import List, Union

import cv2
import jaitool.inference.d2_infer
import numpy as np
import pandas as pd
import printj
import pyjeasy.file_utils as f
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from jaitool.draw import draw_bbox, draw_keypoints, draw_mask_bool
from jaitool.structures.bbox import BBox
from jaitool.structures.point import Point2D
from pyjeasy.check_utils import check_value
from pyjeasy.check_utils.check import check_file_exists  # pip install printj
from pyjeasy.file_utils import (delete_dir, delete_dir_if_exists, dir_exists,
                                dir_files_list, file_exists, make_dir,
                                make_dir_if_not_exists)
from pyjeasy.image_utils import show_image
from seaborn import color_palette
from tqdm import tqdm


def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1


class D2Inferer:
    def __init__(
            self,
            weights_path: str,
            class_names: List[str] = None, num_classes: int = None,
            keypoint_names: List[str] = None, num_keypoints: int = None,
            model: str = "mask_rcnn_R_50_FPN_1x",
            confidence_threshold: float = 0.5,
            size_min: int = None,
            size_max: int = None,
            key_seg_together: bool = False,
            gray_on=False,
            crop_mode: int = None,
            crop_mode2_rec: Union[int, List[int]] = None,
            crop_mode3_sizes: Union[int, List[int]] = None,
            crop_mode3_overlaps: Union[int, List[int]] = None,
            detectron2_dir_path: str = "/home/jitesh/detectron/detectron2"
    ):
        """
        D2Inferer
        =========

        Parameters:
        ------
        - weights_path: str 
        - class_names: List[str] = None, num_classes: int = None,
        - keypoint_names: List[str] = None, num_keypoints: int = None,
        - model: str = "mask_rcnn_R_50_FPN_1x",
        - confidence_threshold: float = 0.5,
        - size_min: int = None,
        - size_max: int = None,
        - key_seg_together: bool = False,
        - detectron2_dir_path: str = "/home/jitesh/detectron/detectron2"

        - crop_mode = 1 : crop between points (0, 0) and (a, a), where a is min(height, width)
        - crop_mode = 2 : crop between points crop_rec[0] and crop_rec[1], crop_rec is defined by the user through parameter
        - crop_mode = 3 : chop, infer and merge
        - crop_rec : list of points of rectangle to crop
        """
        self.df = pd.DataFrame(data=[], columns=[])
        self.gray_on = gray_on
        self.crop_mode = crop_mode
        self.crop_rec = crop_mode2_rec
        self.crop_mode3_sizes = crop_mode3_sizes
        self.crop_mode3_overlaps = crop_mode3_overlaps
        if class_names is None:
            class_names = ['']
        if keypoint_names is None:
            keypoint_names = ['']
        self.key_seg_together = key_seg_together
        self.weights_path = weights_path
        self.class_names = class_names
        if num_classes is None:
            self.num_classes = len(class_names)
        else:
            assert num_classes == len(class_names)
            self.num_classes = num_classes
        self.keypoint_names = keypoint_names
        if num_keypoints is None:
            self.num_keypoints = len(keypoint_names)
        else:
            assert num_keypoints == len(keypoint_names)
            self.num_keypoints = num_keypoints
        self.confidence_threshold = confidence_threshold
        self.model = model
        if "COCO-Detection" in self.model:
            self.model = self.model
        elif "COCO-Keypoints" in self.model:
            self.model = self.model
        elif "COCO-InstanceSegmentation" in self.model:
            self.model = self.model
        elif "COCO-PanopticSegmentation" in self.model:
            self.model = self.model
        elif "LVIS-InstanceSegmentation" in self.model:
            self.model = self.model
        elif "Misc" in model:
            self.model = model
            # train_type = 'seg'
        elif "rpn" in model:
            self.model = "COCO-Detection/" + model
        elif "keypoint" in model:
            self.model = "COCO-Keypoints/" + model
        elif "mask" in model:
            self.model = "COCO-InstanceSegmentation/" + model
        else:
            printj.red.bold_on_black(f'{model} is not in the dictionary.\
                Choose the correct model.')
            raise Exception

        if ".yaml" in self.model:
            self.model = self.model
        else:
            self.model = self.model + ".yaml"

        self.cfg = get_cfg()
        model_conf_path = f"{detectron2_dir_path}/configs/{self.model}"
        if not file_exists(model_conf_path):
            printj.red(f"Invalid model: {model}\nOr")
            printj.red(f"File not found: {model_conf_path}")
            raise Exception
        self.cfg.merge_from_file(model_conf_path)
        self.cfg.MODEL.WEIGHTS = self.weights_path
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = self.num_classes
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.confidence_threshold
        self.cfg.MODEL.ROI_KEYPOINT_HEAD.NUM_KEYPOINTS = self.num_keypoints
        if "mask" in self.model.lower() or "segmentation" in self.model.lower():
            self.cfg.MODEL.MASK_ON = True
        # self.cfg.MODEL.SEM_SEG_HEAD.LOSS_WEIGHT=0.5
        if size_min is not None:
            self.cfg.INPUT.MIN_SIZE_TRAIN = size_min
            self.cfg.INPUT.MIN_SIZE_TEST = size_min
        if size_max is not None:
            self.cfg.INPUT.MAX_SIZE_TRAIN = size_max
            self.cfg.INPUT.MAX_SIZE_TEST = size_max
        self.predictor = DefaultPredictor(self.cfg)
        self.pred_dataset = []
        self.palette = np.array(color_palette(
            palette='hls', n_colors=self.num_classes+1))*255

    def get_outputs(self, img: np.ndarray) -> dict:
        ''''''
        return self.predictor(img)

    def predict(self, img: np.ndarray) -> dict:
        """
        predict_dict = self.predict(img=img)

        score_list = predict_dict['score_list']

        bbox_list = predict_dict['bbox_list']

        pred_class_list = predict_dict['pred_class_list']

        pred_masks_list = predict_dict['pred_masks_list']

        pred_keypoints_list = predict_dict['pred_keypoints_list']

        vis_keypoints_list = predict_dict['vis_keypoints_list']

        kpt_confidences_list = predict_dict['kpt_confidences_list']

        for score, pred_class, bbox, mask, keypoints, vis_keypoints, kpt_confidences in zip(score_list,
                                                                                            pred_class_list,
                                                                                            bbox_list,
                                                                                            pred_masks_list,
                                                                                            pred_keypoints_list,
                                                                                            vis_keypoints_list,
                                                                                            kpt_confidences_list):
        """
        if self.gray_on:
            gray = cv2.cvtColor(img.copy(), cv2.COLOR_RGB2GRAY)
            img = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

        outputs = self.get_outputs(img)
        result = dict()
        score_list = [float(val)
                      for val in outputs['instances'].scores.cpu().numpy()]
        bbox_list = [BBox.from_list(val_list).to_int() for val_list in
                     outputs['instances'].pred_boxes.tensor.cpu().numpy()]
        pred_class_list = [self.class_names[idx]
                           for idx in outputs['instances'].pred_classes.cpu().numpy()]
        if self.cfg.MODEL.MASK_ON:
            pred_masks_list = [mask
                               for mask in outputs['instances'].pred_masks.cpu().numpy()]
        else:
            pred_masks_list = [None] * len(score_list)
        if 'keypoint' in self.model.lower():
            pred_keypoints_list = [keypoints
                                   for keypoints in outputs['instances'].pred_keypoints.cpu().numpy()]

            vis_keypoints_list = [[[int(x), int(y)] for x, y, c in keypoints]
                                  for keypoints in pred_keypoints_list]
            kpt_confidences_list = [[c for x, y, c in keypoints]
                                    for keypoints in pred_keypoints_list]
        else:
            pred_keypoints_list = [None] * len(score_list)
            vis_keypoints_list = [None] * len(score_list)
            kpt_confidences_list = [None] * len(score_list)
        result['score_list'] = score_list
        result['bbox_list'] = bbox_list
        result['pred_class_list'] = pred_class_list
        result['pred_masks_list'] = pred_masks_list
        result['pred_keypoints_list'] = pred_keypoints_list
        result['vis_keypoints_list'] = vis_keypoints_list
        result['kpt_confidences_list'] = kpt_confidences_list
        return result

    @staticmethod
    def confirm_folder(path, mode):
        '''Deletes the directory if exist and create new directory.'''
        # make_dir_if_not_exists(path)
        if mode == 'save':
            if dir_exists(path):
                delete_dir(path)
                make_dir(path)
            else:
                make_dir(path)

    def chop_and_fix(
        self,
        img,
        c_sizes=[1024],
        c_overlaps=[100],
        padding_color=[255, 255, 255],
    ):
        img_h, img_w, _c = img.shape
        img = cv2.copyMakeBorder(
            img, top=0, bottom=max(c_sizes), left=0, right=max(c_sizes),
            borderType=cv2.BORDER_CONSTANT, value=padding_color)
        result = dict()
        result['score_list'] = []
        result['bbox_list'] = []
        result['pred_class_list'] = []
        result['pred_masks_list'] = []
        result['pred_keypoints_list'] = []
        result['vis_keypoints_list'] = []
        result['kpt_confidences_list'] = []
        # all_score_list = []
        # all_bbox_list = []
        # all_pred_class_list = []
        # all_pred_masks_list = []
        # all_pred_keypoints_list = []
        # all_vis_keypoints_list = []
        # all_kpt_confidences_list = []
        for c_size, c_overlap in zip(c_sizes, c_overlaps):
            i = 0
            h = 0
            while h < img_h:
                sys.stdout.write(f"\rCreating image {i} if size {c_size}")
                sys.stdout.flush()
                w = 0
                while w < img_w:
                    c_img = img[h:h+c_size, w:w+c_size, :]
                    predict_dict = self.predict(img=c_img)
                    score_list = predict_dict['score_list']
                    bbox_list = predict_dict['bbox_list']
                    pred_class_list = predict_dict['pred_class_list']
                    pred_masks_list = predict_dict['pred_masks_list']
                    pred_keypoints_list = predict_dict['pred_keypoints_list']
                    vis_keypoints_list = predict_dict['vis_keypoints_list']
                    kpt_confidences_list = predict_dict['kpt_confidences_list']
                    new_bbox_list = []
                    for bbox in bbox_list:
                        new_bbox = bbox + Point2D.from_list([w, h])
                        new_bbox_list.append(new_bbox)

                    result['score_list'] += score_list
                    result['bbox_list'] += new_bbox_list
                    result['pred_class_list'] += pred_class_list
                    result['pred_masks_list'] += pred_masks_list
                    result['pred_keypoints_list'] += pred_keypoints_list
                    result['vis_keypoints_list'] += vis_keypoints_list
                    result['kpt_confidences_list'] += kpt_confidences_list
                    # for bbox in bbox_list:
                    # print(bbox_list)
                    # if show_image(c_img, f"size: {c_size}, horizntal: {w}-{w+c_size}, vertical: {h}-{h+c_size}", 900):
                    #     return
                    # output = os.path.join(output_path, f't_{c_size}_{i}.jpg')
                    # useful_img = lbm.create_cropped_labelme(
                    #     c_point1=[w, h],
                    #     c_point2=[w+c_size, h+c_size],
                    #     output_img=f'{output}',
                    #     theshold=theshold)
                    i += 1
                    w += c_size - c_overlap
                h += c_size - c_overlap
        # return all_score_list, all_bbox_list, all_pred_class_list, all_pred_masks_list, all_pred_keypoints_list, all_vis_keypoints_list, all_kpt_confidences_list
        return result

    def _infer_image(self, image_path: str,
                     show_max_score_only: bool = False,
                     show_class_label: bool = True,
                     show_class_label_score_only: bool = False,
                     show_keypoint_label: bool = True,
                     show_bbox: bool = True,
                     show_keypoints: bool = True,
                     show_segmentation: bool = True,
                     color_bbox: list = None,
                     transparent_mask: bool = True,
                     transparency_alpha: float = 0.3,
                     ignore_keypoint_idx=None,
                     show_legends: bool = False,
                     # gt_path: str = None,
                     ) -> np.ndarray:
        '''Returns the Inference result of a single image.'''
        _predict_image = partial(
            self.infer_image,
            image_path=image_path,
            show_max_score_only=show_max_score_only,
            show_class_label=show_class_label,
            show_class_label_score_only=show_class_label_score_only,
            show_keypoint_label=show_keypoint_label,
            show_bbox=show_bbox, show_keypoints=show_keypoints, show_segmentation=show_segmentation,
            color_bbox=color_bbox,
            transparent_mask=transparent_mask, transparency_alpha=transparency_alpha,
            ignore_keypoint_idx=ignore_keypoint_idx,
            show_legends=show_legends
            # gt_path=gt_path
        )
        img = cv2.imread(image_path)
        # if self.gray_on:
        #     gray = cv2.cvtColor(_img, cv2.COLOR_RGB2GRAY)
        #     img = cv2.cvtColor(gray.copy(), cv2.COLOR_GRAY2RGB)
        # else:
        # img = _img
        if self.crop_mode == 1:
            h, w, _ = img.shape
            a = min(h, w)
            img = img[0:a, 0:a]
            output = _predict_image(img)
        elif self.crop_mode == 2:
            p1, p2 = self.crop_rec
            p = BBox.from_list([p1, p2])
            img = img[p.ymin: p.ymax, p.xmin: p.xmax]
            output = _predict_image(img)
        elif self.crop_mode == 3:
            predict_dict = self.chop_and_fix(
                img, self.crop_mode3_sizes, self.crop_mode3_overlaps)
            if self.filter_prediction:
                predict_dict = self.filter_predictions(predict_dict)

            score_list = predict_dict['score_list']
            bbox_list = predict_dict['bbox_list']
            pred_class_list = predict_dict['pred_class_list']
            pred_masks_list = predict_dict['pred_masks_list']
            pred_keypoints_list = predict_dict['pred_keypoints_list']
            vis_keypoints_list = predict_dict['vis_keypoints_list']
            kpt_confidences_list = predict_dict['kpt_confidences_list']
            output = img
            output = self.draw_infer(show_max_score_only, show_class_label, show_class_label_score_only, show_keypoint_label, show_bbox, show_keypoints, show_segmentation, color_bbox, transparent_mask,
                                     transparency_alpha, ignore_keypoint_idx, output, score_list, bbox_list, pred_class_list, pred_masks_list, pred_keypoints_list, vis_keypoints_list, kpt_confidences_list,
                                     show_legends)
            # return output

        else:
            output = _predict_image(img)

        return output

    def infer_image(self,
                    img: str = None,
                    image_path: str = None,
                    show_max_score_only: bool = False,
                    show_class_label: bool = True,
                    show_class_label_score_only: bool = False,
                    show_keypoint_label: bool = True,
                    show_bbox: bool = True,
                    show_keypoints: bool = True,
                    show_segmentation: bool = True,
                    color_bbox: list = None,
                    transparent_mask: bool = True,
                    transparency_alpha: float = 0.3,
                    ignore_keypoint_idx=None,
                    show_legends: bool = False,
                    # gt_path: str = None,
                    ) -> np.ndarray:
        '''Returns the Inference result of a single image.'''
        if ignore_keypoint_idx is None:
            ignore_keypoint_idx = []
        # img = cv2.imread(image_path)
        # # show_image(img)

        # if self.gray_on:
        #     gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        #     img = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        # if self.crop_mode == 1:
        #     h, w, _ = img.shape
        #     a = min(h, w)
        #     img = img[0:a, 0:a]
        #     # img = img[1000:h, 1000:h]
        # if self.crop_mode == 2:
        #     p1, p2 = self.crop_rec
        #     img = img[p1[1]:p2[1], p1[0]:p2[0]]
        # if self.crop_mode == 3:
        #     return
        output = img.copy()
        predict_dict = self.predict(img=img)

        if self.filter_prediction:
            predict_dict = self.filter_predictions(predict_dict)

        status_gt, output = self.draw_gt(image_path.split("/")[-1], output)
        # if not status_gt:
        #     printj.green(status_gt)
        #     output = cv2.imread(image_path)
        score_list = predict_dict['score_list']
        bbox_list = predict_dict['bbox_list']
        pred_class_list = predict_dict['pred_class_list']
        pred_masks_list = predict_dict['pred_masks_list']
        pred_keypoints_list = predict_dict['pred_keypoints_list']
        vis_keypoints_list = predict_dict['vis_keypoints_list']
        kpt_confidences_list = predict_dict['kpt_confidences_list']
        # printj.cyan(predict_dict['bbox_list'])

        output = self.draw_infer(show_max_score_only, show_class_label, show_class_label_score_only, show_keypoint_label,
                                 show_bbox, show_keypoints, show_segmentation, color_bbox, transparent_mask,
                                 transparency_alpha, ignore_keypoint_idx, output, score_list, bbox_list, pred_class_list,
                                 pred_masks_list, pred_keypoints_list, vis_keypoints_list, kpt_confidences_list, show_legends)

        return output

    def draw_infer(self, show_max_score_only, show_class_label, show_class_label_score_only, show_keypoint_label,
                   show_bbox, show_keypoints, show_segmentation, color_bbox, transparent_mask, transparency_alpha,
                   ignore_keypoint_idx, output, score_list, bbox_list, pred_class_list, pred_masks_list, pred_keypoints_list,
                   vis_keypoints_list, kpt_confidences_list, show_legends=False):
        if self.gt_path is None:
            self.img_id_without_gt = next(self.counter)
        max_score_list = dict()
        max_score_pred_list = dict()
        output = output.copy()
        if show_max_score_only:
            for i, class_name in enumerate(self.class_names):
                max_score_list[class_name] = -1
        # Setting color palletes/ class name legend on top left side of the image if color_bbox is None:
        if color_bbox is None:
            if show_legends:
                for i, name in enumerate(self.class_names):
                    scale = 2
                    if scale == 1:
                        cv2.putText(
                            img=output, text=name,
                            # org=(5, 30 + 30*i),
                            # org=(5, 100 + 70*i),
                            org=(5, output.shape[0]-(200 + 30*i)),
                            # org=(5, output.shape[0]-(100 + 70*i)),
                            fontFace=cv2.FONT_HERSHEY_COMPLEX,
                            fontScale=1, color=self.palette[i],
                            thickness=1, bottomLeftOrigin=False)
                    elif scale == 2:
                        cv2.putText(
                            img=output, text=name,
                            org=(5, output.shape[0]-(100 + 70*i)),
                            fontFace=cv2.FONT_HERSHEY_COMPLEX,
                            fontScale=2, color=self.palette[i],
                            thickness=2, bottomLeftOrigin=False)

        for score, pred_class, bbox, mask, keypoints, vis_keypoints, kpt_confidences in zip(score_list,
                                                                                            pred_class_list,
                                                                                            bbox_list,
                                                                                            pred_masks_list,
                                                                                            pred_keypoints_list,
                                                                                            vis_keypoints_list,
                                                                                            kpt_confidences_list):
            cat_id = self.class_names.index(pred_class)
            if color_bbox:
                _color_bbox = color_bbox
            else:
                _color_bbox = self.palette[cat_id]
            """
            # _box = BBox(
            #     # bbox.xmin, bbox.ymin, 
            #     bbox.xmin-int(bbox.width/4), bbox.ymin-int(bbox.height/4), 
            #     bbox.xmax+bbox.width, bbox.ymax+int(bbox.height*3/4))
            # printj.red(_box)
            # check_text_frame = img.copy()[_box.ymin:_box.ymax, _box.xmin:_box.xmax]
            # # check_text_frame = cv2.adaptiveThreshold(check_text_frame,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            # # cv2.THRESH_BINARY,5,2)*3
            # # blur = cv2.GaussianBlur(check_text_frame,(5,5),0)
            # # ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            # template_path = "/home/jitesh/prj/SekisuiProjects/test/gosar/tm/t.jpg"
            # cv2.imwrite(template_path, check_text_frame)
            # gray = cv2.cvtColor(check_text_frame, cv2.COLOR_BGR2GRAY)
            # # gray = cv2.medianBlur(gray, 3)
            # # gray = check_text_frame
            # config = ('-l eng --oem 1 --psm 3')
            # # # pytessercat
            # import pytesseract
            # text = pytesseract.image_to_string(gray, config=config)
            # boxes = pytesseract.image_to_boxes(gray, config=config)
            # print(boxes)
            # _text = text.split('\n')
            # print(_text)
            # _img = cv2.copyMakeBorder(check_text_frame, top=100, bottom=0, left=0, right=200, borderType=0)
            # cv2.putText(_img, text, (10, 30), fontFace= cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=[255, 255, 255], thickness=1, lineType=1)
            
            # cv2.putText(_img, str(boxes), (10, 60), fontFace= cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=[255, 255, 255], thickness=1, lineType=1)
            # if show_image(_img):
            #     return
            """
            # if pred_class in ["switch"]:
            if True:
                if show_max_score_only:
                    for i, class_name in enumerate(self.class_names):
                        if class_name == pred_class:
                            if max_score_list[class_name] < score:
                                max_score_list[class_name] = score
                                max_score_pred_list[class_name] = {
                                    "score": score,
                                    "pred_class": pred_class,
                                    "bbox": bbox,
                                    "mask": mask,
                                    "keypoints": keypoints,
                                    "vis_keypoints": vis_keypoints,
                                    "kpt_confidences": kpt_confidences,
                                }
                else:
                    if mask is not None and show_segmentation:
                        output = draw_mask_bool(img=output, mask_bool=mask, transparent=transparent_mask,
                                                alpha=transparency_alpha)
                    if show_class_label_score_only:
                        output = draw_bbox(img=output, bbox=bbox, color=_color_bbox,
                                           show_bbox=show_bbox, show_label=show_class_label, text=f'{round(score, 2)}')
                    else:
                        output = draw_bbox(img=output, bbox=bbox, color=_color_bbox,
                                           show_bbox=show_bbox, show_label=show_class_label, text=f'{pred_class}', label_orientation='right')
                        output = draw_bbox(img=output, bbox=bbox, color=_color_bbox,
                                           show_bbox=show_bbox, show_label=show_class_label, text=f'{round(score, 2)}')
                    if keypoints is not None and show_keypoints:
                        output = draw_keypoints(img=output, keypoints=keypoints, show_keypoints=show_keypoints,
                                                keypoint_labels=self.keypoint_names, show_keypoints_labels=show_keypoint_label,
                                                ignore_kpt_idx=ignore_keypoint_idx)
                    xmin, ymin, xmax, ymax = bbox.to_int().to_list()
                    pred_to_append = dict()
                    if self.gt_path:
                        for category in self.gt_data["categories"]:
                            if category["name"] == pred_class:
                                cat_id = category["id"]
                        pred_to_append["image_id"] = self.image_id
                        pred_to_append["category_id"] = cat_id
                    else:
                        pred_to_append["image_id"] = self.img_id_without_gt
                        pred_to_append["category_id"] = cat_id
                    pred_to_append["bbox"] = BBox(
                        xmin, ymin, xmax, ymax).to_list(output_format='pminsize')
                    if keypoints:
                        _k = []
                        for keypoint in keypoints:
                            # printj.red(keypoint)
                            x, y, c = keypoint
                            _k.append(int(x))
                            _k.append(int(y))
                            _k.append(1)
                        pred_to_append["keypoints"] = _k
                    pred_to_append["score"] = score
                    self.pred_dataset.append(pred_to_append)
                    # printj.red(keypoints)
            if show_max_score_only:
                for i, class_name in enumerate(self.class_names):
                    cat_id = self.class_names.index(class_name)
                    if color_bbox:
                        _color_bbox = color_bbox
                    else:
                        _color_bbox = self.palette[cat_id]
                    if max_score_list[class_name] > 0:
                        max_pred = max_score_pred_list[class_name]
                        if max_pred["mask"] is not None and show_segmentation:
                            output = draw_mask_bool(img=output, mask_bool=max_pred["mask"], color=_color_bbox, transparent=transparent_mask,
                                                    alpha=transparency_alpha)
                        output = draw_bbox(img=output, bbox=max_pred["bbox"],
                                           show_bbox=show_bbox, show_label=show_class_label, text=f'{max_pred["pred_class"]} {round(max_pred["score"], 2)}')
                        if max_pred["keypoints"] is not None and show_keypoints:
                            output = draw_keypoints(img=output, keypoints=max_pred["keypoints"], show_keypoints=show_keypoints,
                                                    keypoint_labels=self.keypoint_names, show_keypoints_labels=show_keypoint_label,
                                                    ignore_kpt_idx=ignore_keypoint_idx)
        return output

    def filter_predictions(self, predict_dict, iou_thres1=0.5, iou_thres2=0.1):
        """
        Returns the predictions after removing overlapping bounding boxes.
        - iou_thres1: to remove redundant overlap
        - iou_thres2: to remove overlap caused by "chop and merge"
        """

        score_list = predict_dict['score_list']
        bbox_list = predict_dict['bbox_list']
        pred_class_list = predict_dict['pred_class_list']
        pred_masks_list = predict_dict['pred_masks_list']
        pred_keypoints_list = predict_dict['pred_keypoints_list']
        vis_keypoints_list = predict_dict['vis_keypoints_list']
        kpt_confidences_list = predict_dict['kpt_confidences_list']
        remove_idxs = []
        for i in range(len(score_list)-1):
            if i in remove_idxs:
                continue
            for j in range(i+1, len(score_list)):
                if j in remove_idxs:
                    continue
                iou = BBox.iou(bbox_list[i], bbox_list[j])
                if iou > iou_thres1:
                    if score_list[i] > score_list[j]:
                        remove_idxs.append(j)
                    else:
                        remove_idxs.append(i)
                elif iou > iou_thres2:
                    if pred_class_list[i] == pred_class_list[j]:
                        if bbox_list[i].area > bbox_list[j].area:
                            remove_idxs.append(j)
                        else:
                            remove_idxs.append(i)
                # print(i, j, round(iou, 3), remove_idxs)
        score_list_filtered = []
        bbox_list_filtered = []
        pred_class_list_filtered = []
        pred_masks_list_filtered = []
        pred_keypoints_list_filtered = []
        vis_keypoints_list_filtered = []
        kpt_confidences_list_filtered = []
        for i in range(len(score_list)):
            if i in remove_idxs:
                continue
            score_list_filtered.append(score_list[i])
            bbox_list_filtered.append(bbox_list[i])
            pred_class_list_filtered.append(pred_class_list[i])
            pred_masks_list_filtered.append(pred_masks_list[i])
            pred_keypoints_list_filtered.append(pred_keypoints_list[i])
            vis_keypoints_list_filtered.append(vis_keypoints_list[i])
            kpt_confidences_list_filtered.append(kpt_confidences_list[i])
        predict_dict['score_list'] = score_list_filtered
        predict_dict['bbox_list'] = bbox_list_filtered
        predict_dict['pred_class_list'] = pred_class_list_filtered
        predict_dict['pred_masks_list'] = pred_masks_list_filtered
        predict_dict['pred_keypoints_list'] = pred_keypoints_list_filtered
        predict_dict['vis_keypoints_list'] = vis_keypoints_list_filtered
        predict_dict['kpt_confidences_list'] = kpt_confidences_list_filtered
        return predict_dict

    def infer(self, input_type: Union[str, int],
              output_type: Union[str, int],
              input_path: Union[str, List[str]],
              output_path: Union[str, List[str]],
              show_max_score_only: bool = False,
              show_class_label: bool = True,
              show_class_label_score_only: bool = False,
              show_keypoint_label: bool = True,
              show_legends: bool = False,
              show_bbox: bool = True,
              show_keypoints: bool = True,
              show_segmentation: bool = True,
              color_bbox: list = None,
              transparent_mask: bool = True,
              transparency_alpha: float = 0.3,
              ignore_keypoint_idx=None,
              filter_predictions: bool = False,
              gt_path: Union[str, List[str]] = None,
              result_json_path: str = None):
        """

        Valid options for,
        === 
        input_type:
        --- 
        ["image", "image_list", "image_directory", "image_directories_list", "video",
        "video_list", "video_directory" ]

        output_type: 
        ---
        ["return_summary", "show_image", "write_image", "write_video" ]

        Returns
        ---
        The inference result of all data formats.
        """
        self.filter_prediction = filter_predictions
        self.counter = infinite_sequence()
        check_value(input_type,
                    check_from=["image", "image_list", "image_directory", "image_directories_list", "video",
                                "video_list", "video_directory"])
        check_value(value=output_type, check_from=[
                    "show_image", "write_image", "write_video"])
        self.gt_path = gt_path
        if self.gt_path:
            check_file_exists(gt_path)
            with open(gt_path) as json_file:
                self.gt_data = json.load(json_file)
        if result_json_path is None:
            if dir_exists(output_path):
                self.result_json_path = f'{output_path}/result.json'
            else:
                _p = output_path.split('.')
                _output_path = '.'.join(_p[:-1])
                self.result_json_path = f'{_output_path}.json'

        predict_image = partial(self._infer_image,
                                show_max_score_only=show_max_score_only,
                                show_class_label=show_class_label,
                                show_class_label_score_only=show_class_label_score_only,
                                show_keypoint_label=show_keypoint_label,
                                show_bbox=show_bbox, show_keypoints=show_keypoints, show_segmentation=show_segmentation,
                                color_bbox=color_bbox,
                                transparent_mask=transparent_mask, transparency_alpha=transparency_alpha,
                                ignore_keypoint_idx=ignore_keypoint_idx,
                                show_legends=show_legends
                                # gt_path=gt_path,
                                )
        if input_type == "image":
            if file_exists(input_path):
                output = predict_image(input_path)
            else:
                raise Error
            if output_type == "return_summary":
                return self.pred_dataset
            elif output_type == "show_image":
                show_image(output)
            elif output_type == "write_image":
                cv2.imwrite(f'{output_path}', output)
            elif output_type == "write_video":
                raise NotImplementedError
            else:
                raise Exception
        elif input_type == "image_list":
            for image_path in tqdm(input_path, colour='#66cc66'):
                output = predict_image(image_path)
                if output_type == "show_image":
                    if show_image(output):
                        break
                elif output_type == "write_image":
                    make_dir_if_not_exists(output_path)
                    filename = f.get_filename(image_path)
                    cv2.imwrite(f'{output_path}/{filename}', output)
                elif output_type == "write_video":
                    raise NotImplementedError
                else:
                    raise Exception
        elif input_type == "image_directory":
            image_path_list = f.dir_contents_path_list_with_extension(
                dirpath=input_path,
                extension=[".png", ".jpg", ".jpeg"])
            for image_path in tqdm(image_path_list, colour='#66cc66'):
                output = predict_image(image_path)
                # output = self.draw_gt(gt_path, gt_data, image_path, output)
                if output_type == "show_image":
                    if show_image(output):
                        break
                elif output_type == "write_image":
                    make_dir_if_not_exists(output_path)
                    filename = f.get_filename(image_path)
                    cv2.imwrite(f'{output_path}/{filename}', output)
                elif output_type == "write_video":
                    raise NotImplementedError
                else:
                    raise Exception
        elif input_type == "image_directories_list":
            for image_directory in tqdm(input_path):
                image_path_list = f.dir_contents_path_list_with_extension(
                    dirpath=input_path,
                    extension=[".png", ".jpg", ".jpeg"])
                for image_path in tqdm(image_path_list, colour='#66cc66'):
                    output = predict_image(image_path)
                    if output_type == "show_image":
                        if show_image(output):
                            break
                    elif output_type == "write_image":
                        filename = f.get_filename(image_path)
                        directory_name = f.get_directory_name(image_path)
                        if f.dir_exists(f'{output_path}/{directory_name}'):
                            f.delete_all_files_in_dir(
                                f'{output_path}/{directory_name}')
                        else:
                            f.make_dir(f'{output_path}/{directory_name}')
                        cv2.imwrite(
                            f'{output_path}/{directory_name}/{filename}', output)
                    elif output_type == "write_video":
                        raise NotImplementedError
                    else:
                        raise Exception
        elif input_type == "video":
            raise NotImplementedError
        elif input_type == "video_list":
            raise NotImplementedError
        elif input_type == "video_directory":
            raise NotImplementedError
        else:
            raise Exception
        # printj.cyan(self.pred_dataset)
        self.write_predictions_json()
        if self.gt_path:
            # print(self.df)
            # pip install openpyxl
            self.df.to_excel(os.path.abspath(
                f'{result_json_path}/../test_data.xlsx'))
            # with open(f"{os.path.abspath(f'{result_json_path}/..')}/test_data.json", 'w') as outfile:
            #     json.dump(self.df, outfile, indent=4)
            # with open('names.csv', 'w', newline='') as csvfile:
            #     # fieldnames = ['first_name', 'last_name']
            #     writer = csv.DictWriter(csvfile,
            #                             # fieldnames=fieldnames
            #                             )

    def write_predictions_json(self):
        try:
            with open(self.result_json_path, 'w+') as outfile:
                json.dump(self.pred_dataset, outfile, indent=4)
            printj.cyan(
                f'Created inference result file: {self.result_json_path}')
        except NotADirectoryError:
            printj.red(f'Not a directory: {self.result_json_path}')

    def draw_gt(self, image_name, output):
        if self.gt_path:
            row = dict()
            for image in self.gt_data["images"]:
                if image["file_name"] == image_name:
                    self.image_id = image["id"]
                    row = {'img_name': image["file_name"],
                           'width': image["width"],
                           'height': image["height"],
                           }
            for ann in self.gt_data["annotations"]:
                if ann["image_id"] == self.image_id:
                    gt_bbox = BBox.from_list(
                        bbox=ann["bbox"], input_format='pminsize')
                    output = draw_bbox(img=output, bbox=gt_bbox,
                                       show_bbox=True, show_label=False, color=[0, 0, 255], thickness=2)
                    row['bbox_width'] = ann["bbox"][2]
                    row['bbox_height'] = ann["bbox"][3]
                    row['bbox_area_default'] = ann["area"]
                    row['bbox_area_s1500'] = ann["area"] * \
                        (1500*1500)/(row['width']*row['height'])
                    row['bbox_area_s1024'] = ann["area"] * \
                        (1024*1024)/(row['width']*row['height'])
                    row['bbox_area_s800'] = ann["area"] * \
                        (800*800)/(row['width']*row['height'])

                    def seperate_sizes(seperate_type="default"):
                        if row[f'bbox_area_{seperate_type}'] < 32**2:
                            row[f'bbox_size_{seperate_type}'] = 0
                            row[f'bbox_s_{seperate_type}'] = 1
                            row[f'bbox_m_{seperate_type}'] = 0
                            row[f'bbox_l_{seperate_type}'] = 0
                        elif row[f'bbox_area_{seperate_type}'] < 96**2:
                            row[f'bbox_size_{seperate_type}'] = 1
                            row[f'bbox_s_{seperate_type}'] = 0
                            row[f'bbox_m_{seperate_type}'] = 1
                            row[f'bbox_l_{seperate_type}'] = 0
                        else:
                            row[f'bbox_area_{seperate_type}'] = 2
                            row[f'bbox_s_{seperate_type}'] = 0
                            row[f'bbox_m_{seperate_type}'] = 0
                            row[f'bbox_l_{seperate_type}'] = 1
                    seperate_sizes("default")
                    seperate_sizes("s1500")
                    seperate_sizes("s1024")
                    seperate_sizes("s800")

                    def check_size(width, height):
                        if row['width'] == width and row['height'] == height:
                            row[f'{width} x {height}'] = 1
                        else:
                            row[f'{width} x {height}'] = 0

                        if row['width'] == height and row['height'] == width:
                            row[f'{height} x {width}'] = 1
                        else:
                            row[f'{height} x {width}'] = 0

                    check_size(2048, 1536)
                    check_size(1024, 768)
                    check_size(854, 640)
                    check_size(640, 480)

                    self.df = self.df.append(pd.DataFrame(row,
                                                          index=[self.image_id]
                                                          ))

            return 1, output
        else:
            return 0, output


if __name__ == "__main__":

    # palette = color_palette(None, 3)
    # # palette = [int(c*255) for color in palette for c in color]
    # palette = [[int(c*255) for c in color] for color in palette ]
    # printj.red(palette)
    # printj.red(np.array(color_palette(None, 3))*255)
    # x()
    inferer_seg = D2Inferer(
        weights_path='/home/jitesh/3d/data/coco_data/ty1w_coco-data/weights/InstanceSegmentation_R_50_1x_aug_val_1/model_0019999.pth',
        confidence_threshold=0.01,
        class_names=['tropicana'],
        model='mask_rcnn_R_50_FPN_1x',
        size_min=1000, size_max=1000,
    )
    now = datetime.now()
    dt_string3 = now.strftime("%m_%d_%H")
    # infer_dump_dir = f'/home/jitesh/3d/blender/Learning/tropicana/infer_5k_{dt_string3}'
    infer_dump_dir = f'/home/jitesh/3d/blender/Learning/tropicana_yellow/infer_5k_{dt_string3}'
    delete_dir_if_exists(infer_dump_dir)
    make_dir_if_not_exists(infer_dump_dir)

    dir_path = "/home/jitesh/Downloads/Photos (3)"
    # dir_path = "/home/jitesh/3d/blender/Learning/tropicana_yellow/img"
    # dir_path = "/home/jitesh/3d/data/coco_data/tropi1_coco-data/img"
    inferer_seg.infer(input_type="image_directory",
                      output_type="show_image",
                      input_path=dir_path,
                      output_path=infer_dump_dir,
                      show_class_label=True,
                      show_max_score_only=True,
                      transparency_alpha=.9,
                      )
