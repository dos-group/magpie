node_list="wally034 wally035 wally036 wally069 wally050 wally051 wally052 wally053 wally062 wally033"
for node in $node_list; do
	echo "---$node---"
	scp -r ../telegraf/ $node:~/app/
	ssh $node 'sudo service telegraf restart'
	printf "\n"
done
