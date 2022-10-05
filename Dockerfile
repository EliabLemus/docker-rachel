FROM centos:7

LABEL maintainer="eliab.lemus.barrios@gmail.com"
RUN yum makecache fast
RUN yum install -y epel-release nginx
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]