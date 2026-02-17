# Get datasets with different resolution -- X2, X3 and X4
generate_resolution_dataset(){
    local dataset=$1
    command="python3 utils/modify_image.py --dataset_path ./EuRoC/${dataset}/ --image_depth 1"
    #command="python3 utils/modify_image.py --dataset_path ./TUMVI/${dataset}/ --image_depth 1 --dataset TUMVI"
    echo $command
    eval $command
}

#generate_resolution_dataset "room"
#generate_resolution_dataset "corridor"
#generate_resolution_dataset "magistrale"
#generate_resolution_dataset "outdoor"

#generate_resolution_dataset "machine_hall"
#generate_resolution_dataset "vicon"

generate_adc_super_resolution(){
    local prefix=$1  # MH or V1
    local start=$2
    local end=$3
    local dir_name=$4

    cd ../AdcSR/
    for ((i=start; i<=end; i++)); do
        dir=$(printf "%s_%02d" "$prefix" "$i")
        input_path=../CollabAR/EuRoC/${dir_name}/${dir}/mav0/cam0/data/
        output_dir="${dir_name/X4_DTC/adc}"
        output_path=../CollabAR/EuRoC/${output_dir}/${dir}/mav0/cam0/data/
        # For TUM dataset
        #dir=$(printf "dataset-%s%d_512_16" "$prefix" "$i")        
        #input_path=../CollabAR/TUMVI/${dir_name}/${dir}/mav0/cam0/data/
        #output_dir="${dir_name/X4/adc}"
        #output_path=../CollabAR/TUMVI/${output_dir}/${dir}/mav0/cam0/data/
        echo $output_path
        command="python3 test.py --LR_dir ${input_path} --SR_dir ${output_path}"
        echo $command
        eval $command
    done
}

source ../adc/bin/activate
generate_adc_super_resolution MH 1 5 "machine_hall_X4_DTC"
generate_adc_super_resolution V1 1 3 "vicon_X4_DTC"
generate_adc_super_resolution V2 1 3 "vicon_X4_DTC"

#generate_adc_super_resolution room 1 6 "room_X4"
#generate_adc_super_resolution corridor 2 2 "corridor_adc"
#generate_adc_super_resolution magistrale 1 4 "magistrale_adc"
deactivate
