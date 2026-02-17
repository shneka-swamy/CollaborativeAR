# Run ORBSLAM3

cd ORB_SLAM3
# mkdir -p results

run_tum_dataset(){
    local start=$1
    local end=$2
    local dir_name=$3
    local file_name=$4

    for ((i=start; i<=end; i++)); do
        for ((j=0; j<1; j++)); do
            file=${file_name}${i}
         
            ./build/release/bin/mono_inertial_tum_vi Vocabulary/ORBvoc.txt Examples/Monocular-Inertial/TUM-VI.yaml ../TUMVI/${dir_name}/dataset-${file}_512_16/mav0/cam0/data/ Examples/Monocular-Inertial/TimeStamps_TUM_ADC/dataset-${file}_512_16.txt ../TUMVI/${file_name}/dataset-${file}_512_16/mav0/imu0/data.csv 

            echo "current dir is ${PWD}"

            ls tracking_pose.txt

            mkdir -p results_${dir_name}/${file}
            mv tracking_pose.txt results_${dir_name}/${file}/tracking_pose_${file}_${j}.txt

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

#run_tum_dataset 1 4 "magistrale_adc_DTC_bk" "magistrale"
#run_tum_dataset 1 4 "magistrale_X2" "magistrale"
#run_tum_dataset 1 4 "magistrate_X3" "magistrale"
#run_tum_dataset 1 4 "magistrale_X4" "magistrale"
#run_tum_dataset 1 4 "magistrale_drct" "magistrale"
run_tum_dataset 1 4 "magistrale_adc" "magistrale"
#run_tum_dataset 4 4 "magistrale_adc_DTC" "magistrale"

#run_tum_dataset 1 4 "magistrale_jpeg_95" "magistrale"

#run_tum_dataset 1 5 "outdoors" "outdoors"
# run_tum_dataset 1 5 "outdoors_X2" "outdoors"
# run_tum_dataset 1 5 "outdoors_X3" "outdoors"
# run_tum_dataset 1 5 "outdoors_X4" "outdoors"

