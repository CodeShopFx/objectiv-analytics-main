clean:
	# clean up caches
	find core plugins queues trackers transports -type d -name dist -o -name coverage -o -name .npmrc -not -path '*node_modules*'  | xargs rm -rf
	rm -f .npmrc

build: clean
	yarn install && yarn build

deploy: build
	cd verdaccio && make  run
	yarn deploy:verdaccio
