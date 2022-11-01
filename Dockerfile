FROM ubuntu:latest
USER root
LABEL maintainer="eliab.lemus.barrios@gmail.com"
#Variables de entorno
ENV DEBIAN_FRONTEND noninteractive
ENV MODULES_PATH /tmp/rachel_modules
RUN mkdir -p /tmp/installer /var/install_modules/bin
#Provisionamiento
COPY Installer/ /tmp/installer/
COPY entrypoint.sh /usr/bin/

#Instalación de paquetes
RUN apt-get update \
    && apt-get install -y curl net-tools php7.4 \
    python3 python3-apt python3-dbus python3-psutil \
    sudo tzdata vim wget whiptail \
    && apt-get clean
#Permisos
COPY Installer/files/rachel/rachel_sudoers /etc/sudoers.d/rachel
RUN chown root:root /etc/sudoers.d/rachel \
    && chmod 0440 /etc/sudoers.d/rachel \
    && echo '1' > /etc/school-id \ 
    && chmod +x /usr/bin/entrypoint.sh \
    && chmod +x /tmp/installer/installer.py \
    && chmod +x /tmp/installer/install_modules.py \
    && mv /tmp/installer/install_modules.py /var/install_modules/bin/.

#Configuracion
WORKDIR /tmp/installer/
RUN python3 installer.py --kiwix --kolibri --school-id=1 --homepage=rachel.com
RUN sed 's/$fsmods{ $moddir }/$fsmods[ $moddir ]/g' -i /var/www/admin/common.php
RUN apt-get clean

EXPOSE 80 81
ENTRYPOINT [ "/usr/bin/entrypoint.sh" ]
CMD /usr/sbin/apache2ctl -D FOREGROUND