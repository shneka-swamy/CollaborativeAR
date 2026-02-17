cd ./Simulation/FullDevelopment/
mkdir -p results_full

dataset=("MH01" "MH02" "MH03" "MH04" "MH05" "MH01" "MH02" "MH03" "MH04" "MH05" "MH01" "MH02" "MH03" "MH04" "MH05" "MH01" "MH02" "MH03" "MH04" "MH05" "MH01" "MH02" "MH03" "MH04" "MH05" "MH01" "MH02" "MH03" "MH04" "MH05")
#dataset=("V101" "V102" "V103" "V101" "V102" "V103" "V101" "V102" "V103" "V101")
#dataset=("V201" "V202" "V203" "V201" "V202" "V203" "V201" "V202" "V203" "V201")
#dataset=("V101" "V102" "V103" "V201" "V202" "V203" "V101" "V102" "V103" "V201" "V101" "V102" "V103" "V201" "V202" "V203" "V101" "V102" "V103" "V201" "V101" "V102" "V103" "V201" "V202" "V203" "V101" "V102" "V103" "V201")
#dataset=("V101" "MH01" "V102" "MH02" "V103" "MH03" "V201" "MH04" "V202" "MH05" "V203" "MH01" "V102" "MH02" "V103" "MH03" "MH01" "MH04" "MH02" "MH05" "MH03" "V101" "MH01" "V102" "MH02" "V103" "MH03" "V201" "MH04" "V202" "MH05" "V203")

echo "${dataset[@]:0:${i}}"
no_queues=4

for ((i=15; i<=19; i++)); do
  no_usr_results=$((i - 5))
    #no_usr_results=3
    echo "{${no_usr_results}}"
    echo "{$i}"
    cmd=(python3 main.py --datasets "${dataset[@]:0:${i}}" \
        --visibility "${i}" --no_queues "${no_queues}" --no_usr_results "${no_usr_results}")
    "${cmd[@]}" 2>&1 | tee "results_final/MH/result_${i}_${no_queues}_${no_usr_results}.txt"
    echo $command
    eval $command
done
