###########################################################################################
#
# USAGE:
# build with: docker build --no-cache -t arnoduvenhage/nginx-base .
# upload with: docker push arnoduvenhage/nginx-base
# 
###########################################################################################

FROM nginx:1

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

# fetch dependencies
RUN apt-get update &&\
    apt-get -y upgrade &&\
    apt-get install -y build-essential git tree wget software-properties-common &&\
    apt-get -y update &&\
    wget https://nginx.org/download/nginx-1.17.5.tar.gz && tar zxvf nginx-1.17.5.tar.gz &&\
    wget https://ftp.pcre.org/pub/pcre/pcre-8.42.tar.gz && tar xzvf pcre-8.42.tar.gz &&\
    wget https://www.zlib.net/zlib-1.2.11.tar.gz && tar xzvf zlib-1.2.11.tar.gz &&\
    wget https://www.openssl.org/source/openssl-1.1.0h.tar.gz && tar xzvf openssl-1.1.0h.tar.gz &&\
    apt-get install -y perl libperl-dev libgd3 libgd-dev libgeoip1 libgeoip-dev geoip-bin libxml2 libxml2-dev libxslt1.1 libxslt1-dev &&\
    rm -rf /var/lib/apt/lists/*

# build nginx
RUN cd nginx-1.17.5 &&\
    ./configure --prefix=/etc/nginx \ 
            --sbin-path=/usr/sbin/nginx \ 
            --modules-path=/usr/lib/nginx/modules \ 
            --conf-path=/etc/nginx/nginx.conf \
            --error-log-path=/var/log/nginx/error.log \
            --pid-path=/var/run/nginx.pid \
            --lock-path=/var/run/nginx.lock \
            --user=nginx \
            --group=nginx \
            --build=Ubuntu \
            --builddir=nginx-1.15.0 \
            --with-select_module \
            --with-poll_module \
            --with-threads \
            --with-file-aio \
            --with-http_ssl_module \
            --with-http_v2_module \
            --with-http_realip_module \
            --with-http_addition_module \
            --with-http_xslt_module=dynamic \
            --with-http_image_filter_module=dynamic \
            --with-http_geoip_module=dynamic \
            --with-http_sub_module \
            --with-http_dav_module \
            --with-http_flv_module \
            --with-http_mp4_module \
            --with-http_gunzip_module \
            --with-http_gzip_static_module \
            --with-http_auth_request_module \
            --with-http_random_index_module \
            --with-http_secure_link_module \
            --with-http_degradation_module \
            --with-http_slice_module \
            --with-http_stub_status_module \
            --with-http_perl_module=dynamic \
            --with-perl_modules_path=/usr/share/perl/5.26.1 \
            --with-perl=/usr/bin/perl \
            --http-log-path=/var/log/nginx/access.log \
            --http-client-body-temp-path=/var/cache/nginx/client_temp \
            --http-proxy-temp-path=/var/cache/nginx/proxy_temp \
            --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp \
            --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp \
            --http-scgi-temp-path=/var/cache/nginx/scgi_temp \
            --with-mail=dynamic \
            --with-mail_ssl_module \
            --with-stream=dynamic \
            --with-stream_ssl_module \
            --with-stream_realip_module \
            --with-stream_geoip_module=dynamic \
            --with-stream_ssl_preread_module \
            --with-compat \
            --with-pcre=../pcre-8.42 \
            --with-pcre-jit \
            --with-zlib=../zlib-1.2.11 \
            --with-openssl=../openssl-1.1.0h \
            --with-openssl-opt=no-nextprotoneg \
            --with-debug &&\
    make -j4 &&\
    make install

# cleanup    
RUN cd .. &&\
    rm -r nginx-1.17.5

# install Certbot
RUN echo "deb http://deb.debian.org/debian stretch-backports main" | tee -a /etc/apt/sources.list &&\
    apt-get update &&\
    apt-get -y upgrade &&\
    apt-get -y install certbot python-certbot-nginx -t stretch-backports &&\
    rm -rf /var/lib/apt/lists/*

# check nginx and setup modules
RUN cd ~ &&\
    ln -s /usr/lib/nginx/modules /etc/nginx/modules &&\
    nginx -V &&\
    nginx -t

