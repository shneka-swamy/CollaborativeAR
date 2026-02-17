import cv2
import argparse
from pathlib import Path
import glob
from tqdm import tqdm

def argparser():
    parser = argparse.ArgumentParser("Make the image low resolution")
    parser.add_argument("--dataset_path", type=str, help="Path to the folder with the image", required=True)
    parser.add_argument('--image_depth', type=int, help="Depth to the original image", default=0)
    parser.add_argument('--ratio', nargs='+', help="Ratio of resolution reduction", default=[4]) #default=[2, 3, 4])
    parser.add_argument('--image', help="Name of the image; None for full directory", default=None)
    parser.add_argument('--dataset', help="Which dataset is used ", default='EuRoC')
    return parser.parse_args()

def readImage(image_file):
    image = cv2.imread(image_file)
    return image

# Reduce the resolution of the image
def reduce_resolution(image, ratio):
    H, W, _ = image.shape
    # if H % ratio == 0:
    #     n_h = H // ratio
    #     n_w = (n_h * W) // H
    # else:
    #     n_w = W // ratio
    #     n_h = (n_w * H) // W
    
    n_h = (H // (ratio *16)) * 16
    n_w = (n_h * W) // H
    #n_w = 48
    n_w = 160 # This is done because ADCSR requires width as multiple of 4

    resized_image = cv2.resize(image, (n_w, n_h), interpolation=cv2.INTER_CUBIC)
    return resized_image    

def determine_path(depth):
    path_string = ''
    for i in range(depth):
        path_string += '/*'
    return path_string

def main():
    args = argparser()
    dataset = []

    if args.image is None:
        directories = glob.glob(args.dataset_path + determine_path(args.image_depth))
        print("Directories: ", directories)
        for directory in directories:
            if not Path(directory).is_dir():
                continue
            if args.dataset == 'EuRoC' or args.dataset == 'TUMVI':
                add_folders = '/mav0/cam0/data/'
            else:
                add_folders = ''
            directory += add_folders
            print("directory", directory)
            for image in glob.glob(directory + '/*.png'):
                dataset.append(image)

    else:
        assert args.image_depth == 0, "To choose one image give the full path to the image"
        dataset.append(args.dataset_path + args.image)

    for image_file in tqdm(dataset):
        image = readImage(image_file)
        for ratio in args.ratio:
            resized_image = reduce_resolution(image, ratio)
            image_file_split = image_file.split('/')
            image_file_split[-6] = image_file_split[-6] + '_X' + str(ratio) + '_DTC'
            #image_file_split[-6] = image_file_split[-6] + '_DTC'
            new_folder = '/'.join(image_file_split[:-1])
            Path(new_folder).mkdir(parents=True, exist_ok=True)
            new_file = new_folder + '/' + image_file_split[-1]
            cv2.imwrite(new_file, resized_image)

if __name__ == '__main__':
    main()
