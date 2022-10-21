FROM ubuntu:latest
USER root
LABEL maintainer="eliab.lemus.barrios@gmail.com"
ENV DEBIAN_FRONTEND noninteractive
RUN mkdir /tmp/installer
COPY Installer/ /tmp/installer/
COPY entrypoint.sh /usr/bin/
RUN apt-get update \
    && apt-get install -y tzdata wget python3 whiptail python3-apt python3-dbus python3-psutil vim sudo curl php7.4
RUN apt-get clean 

#TODO: Improve school id handle
COPY Installer/files/rachel/rachel_sudoers /etc/sudoers.d/rachel
RUN chown root:root /etc/sudoers.d/rachel \
    && chmod 0440 /etc/sudoers.d/rachel \
    && echo '1' > /etc/school-id \ 
    && chmod +x /usr/bin/entrypoint.sh

RUN chmod +x /tmp/installer/installer.py

WORKDIR /tmp/installer/

# RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
RUN python3 installer.py --kiwix --school-id=1 --homepage=rachel.com
RUN sed 's/$fsmods{ $moddir }/$fsmods[ $moddir ]/g' -i /var/www/admin/common.php

EXPOSE 80 81
ENTRYPOINT [ "/usr/bin/entrypoint.sh" ]
CMD /usr/sbin/apache2ctl -D FOREGROUND