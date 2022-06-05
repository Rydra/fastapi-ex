partitions := 2

create-kafka-topic:
	docker-compose exec broker kafka-topics --bootstrap-server broker:9092 --replication-factor 1 --partitions $(partitions) --create --topic $(topic)
