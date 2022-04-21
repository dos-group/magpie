#! /bin/bash
# read rpc stats
read_rpc_centos(){
  osc_name=$1
  # format: read_rpcs_in_flight, write_rpcs_in_flight, pending_write_pages, pending_read_pages
  rpc_stats=$(lctl get_param $osc_name| tail -n +3 |head -n 4| cut -d':' -f2|awk '{print $1"i"}')
  paste -d'=' <(echo -e "read_rpcs_in_flight\nwrite_rpcs_in_flight\npending_write_pages\npending_read_pages") <(echo "$rpc_stats")|paste -s -d ','
}

#/sys/kernel/debug/lustre/osc/instance_name/rpc_stats

read_rpc_ubuntu(){
  osc_name=$1
  # format: read_rpcs_in_flight, write_rpcs_in_flight, pending_write_pages, pending_read_pages
  rpc_stats=$(cat /sys/kernel/debug/lustre/osc/$osc_name/rpc_stats| tail -n +2 |head -n 4| cut -d':' -f2|awk '{print $1"i"}')
  paste -d'=' <(echo -e "read_rpcs_in_flight\nwrite_rpcs_in_flight\npending_write_pages\npending_read_pages") <(echo "$rpc_stats")|paste -s -d ','
}

if [[ $(lsb_release -d) == *"Ubuntu"* ]]; then
  is_ubuntu=true
else
  is_ubuntu=false
fi

for param_name in $(lctl get_param osc.*.cur_grant_bytes);
do
  osc_name=$(echo $param_name |cut -d. -f2)
  osc_prefix=$(echo $param_name |cut -d. -f1-2)
  osd_id=$(echo $osc_prefix |cut -d- -f2)
  cur_dirty_bytes=$(lctl get_param ${osc_prefix}.cur_dirty_bytes |cut -d= -f2)i
  cur_grant_bytes=$(lctl get_param ${osc_prefix}.cur_grant_bytes |cut -d= -f2)i
  if [[ $(lsb_release -d) == *"Ubuntu"* ]]; then
      rpc_stats=$(read_rpc_ubuntu ${osc_name})
  else
      rpc_stats=$(read_rpc_centos ${osc_prefix}.rpc_stats)
  fi
  echo lustre,osd_id=${osd_id} cur_dirty_bytes=${cur_dirty_bytes},cur_grant_bytes=${cur_grant_bytes},${rpc_stats}
done