import cv2
import os


def figure_cutter(figure_ID_old, figure_ID_new, loc=(0, 0), show_info=False):
    im = cv2.imread(figure_ID_old)
    h, w = im.shape[:2]
    cut_color = im[loc[0], loc[1]]
    top, bottom, left, right = 0, h, 0, w
    for ih in range(h):
        if not (cut_color == im[ih]).all():
            top = ih
            break
    for ih in range(h):
        if not (cut_color == im[h - ih - 1]).all():
            bottom = h - ih
            break
    for iw in range(w):
        if not (cut_color == im[top:bottom, iw]).all():
            left = iw
            break
    for iw in range(w):
        if not (cut_color == im[top:bottom, w - iw - 1]).all():
            right = w - iw
            break
    new = im[top:bottom, left:right]
    cv2.imwrite(figure_ID_new, new)
    if show_info:
        print(f'WxH: {w}x{h} -> {right-left}x{bottom-top}')


def cut_list(fn_old_dir, fn_new_dir, **kwargs):
    os.makedirs(fn_new_dir, exist_ok=True)
    for fn in os.listdir(fn_old_dir):
        figure_cutter(os.path.join(fn_old_dir, fn), os.path.join(fn_new_dir, f'{fn[:-3]}tif'), **kwargs)


if __name__ == '__main__':
    fn0 = 'a.png'
    fn1 = 'a1.tif'
    figure_cutter(fn0, fn1)
