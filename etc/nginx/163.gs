upstream 163gs_upstream {
    server 127.0.0.1:8850;
    server 127.0.0.1:8851;
}

server {
    server_name 163.gs;

    location / {
        proxy_pass http://163gs_upstream;
        proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
    }
}

server {
    server_name www.163.gs;

    return 301 $scheme://163.gs$request_uri;
}
