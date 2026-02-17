# Run ORBSLAM3

cd ORB_SLAM3
# mkdir -p results

run_euroc_dataset() {
    local prefix=$1  # MH or V1
    local start=$2
    local end=$3
    local dir_name=$4
    local timestamp=$5

    for ((i=start; i<=end; i++)); do
	    # for ((j=i+1; j<=5; j++)); do
      for ((j=0; j<5; j++)); do
            dir=$(printf "%s_%02d" "$prefix" "$i")
            file=$(printf "%s%02d" "$prefix" "$i")
            #dir1=$(printf "%s_%02d" "$prefix" "$j")
            #file1=$(printf "%s%02d" "$prefix" "$j")
              
            mkdir -p results_${dir_name}/${file}/
            echo ../EuRoC/${dir_name}/${dir}/ 
            echo Examples/Monocular-Inertial/${timestamp}/${file}.txt 
            #./build/release/bin/mono_inertial_euroc Vocabulary/ORBvoc.txt Examples/Monocular-Inertial/EuRoC.yaml ../EuRoC/${dir_name}/${dir}/ Examples/Monocular-Inertial/${timestamp}/${file}.txt ../EuRoC/${dir_name}/${dir1}/ Examples/Monocular-Inertial/${timestamp}/${file1}.txt 
            ./build/release/bin/mono_inertial_euroc Vocabulary/ORBvoc.txt Examples/Monocular-Inertial/EuRoC.yaml ../EuRoC/${dir_name}/${dir}/ Examples/Monocular-Inertial/${timestamp}/${file}.txt  

            #echo "current dir is ${PWD}"

            #ls tracking_pose.txt

            #mv tracking_pose.txt results_${dir_name}/${file}/tracking_pose_${file}_${j}.txt
            mv LocalMapTimeStats.txt results_${dir_name}/${file}/LocalMapTimeStats_${file}_${file1}_${j}.txt
            mv TrackingTimeStats.txt results_${dir_name}/${file}/TrackingTimeStats_${file}_${file1}_${j}.txt
            mv KeyFrameTrajectory.txt results_${dir_name}/${file}/"KeyFrameTrajectory_"${file}_${file1}_${j}.txt
            mv CameraTrajectory.txt results_${dir_name}/${file}/"CameraTrajectory_"${file}_${file1}_${j}.txt

            command="python3 ./evaluation/evaluate_ate_scale.py ./evaluation/Ground_truth/EuRoC_left_cam/${file}_GT.txt results_${dir_name}/${file}/"CameraTrajectory_"${file}_${file1}_${j}.txt --output_dir ./results_${dir_name}/${file} --output_file ATE_${file}_${j}.txt"
            echo $command
            eval $command

        done    
    done
}

# Run the method for euroc dataset
# run_euroc_dataset "MH" 1 5 "machine_hall_X4_UPSAMPLE" "EuRoC_TimeStamps" 
# run_euroc_dataset "V1" 1 3 "vicon_X4_UPSAMPLE" "EuRoC_TimeStamps" 
# run_euroc_dataset "V2" 1 3 "vicon_X4_UPSAMPLE" "EuRoC_TimeStamps"
 
# # Run the method for different resolutions
#run_euroc_dataset "MH" 1 5 "machine_hall_X2" "EuRoC_TimeStamps" 
#run_euroc_dataset "MH" 1 5 "machine_hall_X3" "EuRoC_TimeStamps" 
#run_euroc_dataset "MH" 1 5 "machine_hall_X4" "EuRoC_TimeStamps" 
#run_euroc_dataset "V1" 1 3 "vicon_X2" "EuRoC_TimeStamps" 
#run_euroc_dataset "V2" 1 3 "vicon_X2" "EuRoC_TimeStamps" 
#run_euroc_dataset "V1" 1 3 "vicon_X3" "EuRoC_TimeStamps" 
#run_euroc_dataset "V2" 1 3 "vicon_X3" "EuRoC_TimeStamps" 
#run_euroc_dataset "V1" 1 3 "vicon_X4" "EuRoC_TimeStamps" 
#run_euroc_dataset "V2" 1 3 "vicon_X4" "EuRoC_TimeStamps" 

# Run the method for super resolution -- DRCT
#run_euroc_dataset "MH" 1 5 "machine_hall_drct" "EuRoC_TimeStamps" 
#run_euroc_dataset "V1" 1 3 "vicon_drct" "EuRoC_TimeStamps" 
#run_euroc_dataset "V2" 3 3 "vicon_drct" "EuRoC_TimeStamps"

# Run the method for super resolution method -- AdcSR
run_euroc_dataset "MH" 1 1 "machine_hall" "EuRoC_TimeStamps"
run_euroc_dataset "V1" 1 3 "vicon_adc" "EuRoC_TimeStamps"
run_euroc_dataset "V2" 1 3 "vicon_adc" "EuRoC_TimeStamps" 

# Run the method for super resolution -- After removing blur
#run_euroc_dataset "MH" 1 1 "machine_hall_drct_no_blur" "TimeStamps_DRCT" 
#run_euroc_dataset "V1" 1 1 "vicon_drct_no_blur" "TimeStamps_DRCT" 
#run_euroc_dataset "V2" 2 2 "vicon_drct_no_blur" "TimeStamps_DRCT"

#run_euroc_dataset "MH" 5 5 "machine_hall_adc_no_blur" "TimeStamps_ADC"
#run_euroc_dataset "V1" 1 1 "vicon_adc_no_blur" "TimeStamps_ADC"
#run_euroc_dataset "V2" 2 2 "vicon_adc_no_blur" "TimeStamps_ADC"

# Run the data with X12 resolution decay and then applying super resolution
#run_euroc_dataset "MH" 1 5 "machine_hall_X12_drct" "EuRoC_TimeStamps" 
#run_euroc_dataset "V1" 1 3 "vicon_X12_drct" "EuRoC_TimeStamps" 
#run_euroc_dataset "V2" 1 3 "vicon_X12_drct" "EuRoC_TimeStamps"

#run_euroc_dataset "MH" 1 5 "machine_hall_X12_adc" "EuRoC_TimeStamps" 
#run_euroc_dataset "V1" 1 1 "vicon_X12_adc" "EuRoC_TimeStamps" 
#run_euroc_dataset "V2" 1 3 "vicon_X12_adc" "EuRoC_TimeStamps"
