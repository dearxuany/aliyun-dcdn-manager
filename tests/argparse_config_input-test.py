#! /usr/local/env python

import argparse

def arg_config_input():

    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument("--gpus", type=str, default="0")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    print(args.gpus)
    print(args.batch_size)


if __name__=="__main__":
    # python argparse_config_input.py --gpus=0,1,2 --batch-size=10
    arg_config_input()

