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
	    for ((j=0; j<5; j++)); do
            dir=$(printf "%s_%02d" "$prefix" "$i")
            file=$(printf "%s%02d" "$prefix" "$i")
            #dir1=$(printf "%s_%02d" "$prefix" "$j")
            #file1=$(printf "%s%02d" "$prefix" "$j")

            echo ../EuRoC/${dir_name}/${dir}/ 
            echo Examples/Monocular-Inertial/${timestamp}/${file}.txt 
            #./build/release/bin/mono_inertial_euroc Vocabulary/ORBvoc.txt Examples/Monocular-Inertial/EuRoC.yaml ../EuRoC/${dir_name}/${dir}/ Examples/Monocular-Inertial/${timestamp}/${file}.txt ../EuRoC/${dir_name}/${dir1}/ Examples/Monocular-Inertial/${timestamp}/${file1}.txt 
            ./build/release/bin/mono_inertial_euroc Vocabulary/ORBvoc.txt Examples/Monocular-Inertial/EuRoC.yaml ../EuRoC/${dir_name}/${dir}/ Examples/Monocular-Inertial/${timestamp}/${file}.txt  i

            mkdir -p results_${dir_name}_sleep_50_final/${file}

            # Determines the ATE value and stores it
            command="python3 ./evaluation/evaluate_ate_scale.py ./evaluation/Ground_truth/EuRoC_left_cam/${file}_GT.txt CameraTrajectory.txt --output_dir ./results_${dir_name}_sleep_50_final/${file} --output_file ATE_${file}_${j}.txt"
            echo $command
            eval $command

            # Moves the trajectories produceb by SLAM
            mv CameraTrajectory.txt results_${dir_name}_sleep_50_final/${file}/CameraTrajectory_${file}_${file1}_${j}.txt   
            mv KeyFrameTrajectory.txt results_${dir_name}_sleep_50_final/${file}/KeyFrameTrajectory_${file}_${file1}_${j}.txt

            # Moves the timing analysis data to a seperate file -- remove this if timing analysis is OFF
            # mv ExecMean.txt results_${dir_name}_timing/${file}/ExecMean_${file}_${file1}_${j}.txt  
            # mv LBA_Stats.txt results_${dir_name}_timing/${file}/LBA_Stats_${file}_${file1}_${j}.txt 
            # mv LocalMapTimeStats.txt results_${dir_name}_timing/${file}/LocalMapTimeStats_${file}_${file1}_${j}.txt
            # mv SessionInfo.txt results_${dir_name}_timing/${file}/SessionInfo_${file}_${file1}_${j}.txt
            # mv TrackingTimeStats.txt results_${dir_name}_timing/${file}/TrackingTimeStats_${file}_${file1}_${j}.txt
            
            #mv atlasFile.osa results/${file}/"atlasFile_"${file}_${j}.osa
        done
    done
}

# Run the method for euroc dataset
run_euroc_dataset "MH" 1 5 "machine_hall" "EuRoC_TimeStamps" 
run_euroc_dataset "V1" 1 3 "vicon" "EuRoC_TimeStamps" 
run_euroc_dataset "V2" 1 3 "vicon" "EuRoC_TimeStamps"

#run_euroc_dataset "MH" 1 5 "machine_hall_jpeg90" "EuRoC_TimeStamps"
#run_euroc_dataset "V1" 1 3 "vicon_jpeg90" "EuRoC_TimeStamps" 
#run_euroc_dataset "V2" 1 3 "vicon_jpeg90" "EuRoC_TimeStamps"

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
#run_euroc_dataset "MH" 1 5 "machine_hall_adc" "EuRoC_TimeStamps"
#run_euroc_dataset "V1" 1 3 "vicon_adc" "EuRoC_TimeStamps"
#run_euroc_dataset "V2" 1 3 "vicon_adc" "EuRoC_TimeStamps" 

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

run_tum_dataset(){
    local start=$1
    local end=$2
    local dir_name=$3
    local file_name=$4

    for ((i=start; i<=end; i++)); do
        for ((j=0; j<1; j++)); do
            file=${file_name}${i}
         
            ./build/release/bin/mono_inertial_tum_vi Vocabulary/ORBvoc.txt Examples/Monocular-Inertial/TUM-VI.yaml ../TUMVI/${dir_name}/dataset-${file}_512_16/mav0/cam0/data/ Examples/Monocular-Inertial/TUM_TimeStamps/dataset-${file}_512.txt ../TUMVI/${file_name}/dataset-${file}_512_16/mav0/imu0/data.csv 

            mkdir -p results_${dir_name}/${file}
            mv CameraTrajectory.txt results_${dir_name}/${file}/CameraTrajectory_${file}_${j}.txt   
            mv KeyFrameTrajectory.txt results_${dir_name}/${file}/KeyFrameTrajectory_${file}_${j}.txt

            # Determines the ATE value and stores it
            command="python3 ./evaluation/evaluate_ate_scale.py ../TUMVI/${file_name}/dataset-${file}_512_16/mav0/mocap0/data.csv results_${dir_name}/${file}/CameraTrajectory_${file}_${j}.txt --output_dir ./results_${dir_name}/${file} --output_file ATE_${file}_${j}.txt"
            echo $command
            eval $command
        done
    done
}

#run_tum_dataset 1 6 "room" "room"
#run_tum_dataset 1 6 "room_X2" "room"
#run_tum_dataset 1 6 "room_X3" "room" 
#run_tum_dataset 1 6 "room_X4" "room"
#run_tum_dataset 1 6 "room_drct" "room"
#run_tum_dataset 1 6 "room_adc" "room"

#run_tum_dataset 1 5 "corridor" "corridor"
#run_tum_dataset 1 5 "corridor_X2" "corridor"
#run_tum_dataset 1 5 "corridor_X3" "corridor"
#run_tum_dataset 1 5 "corridor_X4" "corridor"
#run_tum_dataset 1 5 "corridor_drct" "corridor"
#run_tum_dataset 2 2 "corridor_adc" "corridor"

#run_tum_dataset 1 4 "magistrale" "magistrale"
#run_tum_dataset 1 4 "magistrale_X2" "magistrale"
#run_tum_dataset 1 4 "magistrate_X3" "magistrale"
#run_tum_dataset 1 4 "magistrale_X4" "magistrale"
#run_tum_dataset 1 4 "magistrale_drct" "magistrale"
#run_tum_dataset 1 4 "magistrale_adc" "magistrale"
#run_tum_dataset 4 4 "magistrale_adc_DTC" "magistrale"
#run_tum_dataset 1 4 "magistrale_jpeg_95" "magistrale"

#run_tum_dataset 1 5 "outdoors" "outdoors"
# run_tum_dataset 1 5 "outdoors_X2" "outdoors"
# run_tum_dataset 1 5 "outdoors_X3" "outdoors"
# run_tum_dataset 1 5 "outdoors_X4" "outdoors"
