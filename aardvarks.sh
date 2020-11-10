build () {
    docker build -t cixiri .
}
run () {
    docker run --name cixiri -p 1233:80 -p 1234:443 cixiri
}
cycle () {
    docker kill cixiri
    docker rm cixiri
    docker build -t cixiri .
    docker run --name cixiri -p 1233:80 -p 1234:443 cixiri
}
logs () {
    docker logs cixiri
}
shell () {
    docker exec -it cixiri bash
}
