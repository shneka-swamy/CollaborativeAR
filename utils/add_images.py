import argparse
import glob
import cv2
from tqdm import tqdm

def argparser():
    parser = argparse.ArgumentParser("Add the orginal image for motion blurred images")
    parser.add_argument('--blur_dir', help="Path to the directory from which blurred images are removed")
    parser.add_argument('--original_dir', help="Path to the original directory")
    return parser.parse_args()

def deter_full_path(directory):
    full_path = directory + '/mav0/cam0/data/'
    return full_path

def store_missing_files(files_blur, files_original):
    i = 0
    print(f"Number of files in blurred images {len(files_blur)}")
    print(f"Number of files in the original images {len(files_original)}")
    for j in tqdm(range(0, len(files_original))):
        file_name_blur = files_blur[i].split('/')[-1]
        file_name_original = files_original[j].split('/')[-1]
        if file_name_blur  == file_name_original:
            image = cv2.imread(files_blur[i])
            resized_image = cv2.resize(image, (752, 480), interpolation=cv2.INTER_CUBIC)
            file_name = files_original[j].split('/')[-1]
            blur_directory_list = files_blur[i-1].split('/')[:-1]
            blur_directory = '/'.join(blur_directory_list) 
            blur_image = blur_directory + '/' + file_name
            cv2.imwrite(blur_image, resized_image)             
            i += 1
        else:
            image = cv2.imread(files_original[j])
            file_name = files_original[j].split('/')[-1]
            blur_directory_list = files_blur[i-1].split('/')[:-1]
            blur_directory = '/'.join(blur_directory_list) 
            blur_image = blur_directory + '/' + file_name
            #print("Path to store blur image: ", blur_image)
            cv2.imwrite(blur_image, image)             
def main():
    args = argparser()

    directory_blur = sorted(glob.glob(args.blur_dir+ '*/'))
    directory_original = sorted(glob.glob(args.original_dir + '*/'))

    print("Directories in blurred folder is: ", directory_blur)
    print("Directories in original folder is:", directory_original)

    assert len(directory_blur) == len(directory_original), "The number of folders in both must be the same"
    for i in range(len(directory_blur)):
        full_blur = deter_full_path(directory_blur[i])
        full_original = deter_full_path(directory_original[i])

        files_blur = sorted(glob.glob(full_blur + '/*.png'))
        files_original = sorted(glob.glob(full_original + '/*.png')) 

        store_missing_files(files_blur, files_original)

        files_blur = sorted(glob.glob(full_blur + '/*.png'))
        files_original = sorted(glob.glob(full_original + '/*.png')) 

        print("Number of images in blurred file is: ", len(files_blur))
        print("Total number of images is: ", len(files_original))

        assert len(files_blur) == len(files_original), f"Number of files must be same, Files blur: {len(files_blur)}, Files original: {len(files_original)}"

if __name__ == '__main__':
    main()