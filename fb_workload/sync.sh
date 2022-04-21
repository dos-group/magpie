node_list="wally033 wally062"
for node in $node_list; do
	echo "---$node---"
	ssh $node "rm -rf ~/app/fb_workload/*"
	scp -r ../fb_workload/ $node:~/app/
	ssh $node "find . -type f -name '*.f' -print0 | xargs -0 sed -i 's/wally053/$node/g'"
	printf "\n"
done
