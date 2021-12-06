#!/usr/bin/env python

import argparse
import sys
import os
import cv2
import ffmpeg
import shutil
import math

def get_args():
    parser = argparse.ArgumentParser(prog="still-rm", description="Still frames remover")
    parser.add_argument("input", type=str, help="path to input file")
    parser.add_argument("output", type=str, help="path to output file")
    parser.add_argument("--area", type=str, dest="area", help="compare area. eg: x,y,width,height")
    parser.add_argument("--force", action="store_true", dest="force", help="always remove tmp frames dir first")
    parser.add_argument("--threshold", type=int, dest="threshold", default=500, help="default: 500")
    parser.add_argument("--verbose", '-v', dest="verbose", action="store_true")
    return parser.parse_args()

def main():
    args = get_args()
    if os.path.isfile(args.input):
        input = ffmpeg.input(args.input)
        frames_dir = os.path.dirname(args.input) + '/tmp_frames'
        if args.force:
            shutil.rmtree(frames_dir, True)
        if not os.path.isdir(frames_dir):
            os.makedirs(frames_dir)
            ffmpeg.output(input, frames_dir + '/%04d.jpg', r="2").run()
    else:
        print("input file does not exist")
        return 1

    ranges = get_ranges(frames_dir)
    ranges = ["between(t, %d, %d)" % (x[0],x[1]) for x in ranges]
    video = input.video.filter('select', '+'.join(ranges)).filter('setpts','N/FRAME_RATE/TB')
    audio = input.audio.filter('aselect', '+'.join(ranges)).filter('asetpts', 'N/SR/TB')
    ffmpeg.output(audio, video, args.output).run()
    return 0

def get_ranges(folder):
    args = get_args()
    area = False
    if args.area != None :
        area = [int(x) for x in args.area.split(',')]
    active_start = 0
    still_count = 0
    imgs = sorted(os.listdir(folder))
    total = len(imgs)
    ranges = []
    for i in range(1, total):
        img1 = cv2.imread(folder + '/' + imgs[i-1])
        img2 = cv2.imread(folder + '/' + imgs[i])
        if area:
            diff = cv2.absdiff(
                img1[area[1]:area[1]+area[3], area[0]:area[0]+area[2]],
                img2[area[1]:area[1]+area[3], area[0]:area[0]+area[2]]
            )
        else:
            diff = cv2.absdiff(img1, img2)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        ret, diff = cv2.threshold(diff, 127, 255, cv2.THRESH_TOZERO)
        diff_count = cv2.countNonZero(diff)
        if diff_count < args.threshold :
            if active_start == i-1 :
                active_start = i
            else:
                still_count += 1
        else :
            if still_count > 5 :
                ranges.append([math.floor(active_start/2), math.ceil((i - still_count)/2)])
                active_start = i
            still_count = 0
        if args.verbose :
            print("%s \t diff=%d \t start=%d \t still=%d" % (imgs[i-1], diff_count, active_start, still_count))
    if active_start < total - 2 :
        ranges.append([math.floor(active_start/2), math.ceil((total - still_count)/2)])
    if args.verbose :
        print(ranges)
    return ranges

if __name__ == "__main__":
    sys.exit(main())

