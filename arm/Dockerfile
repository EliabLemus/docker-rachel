FROM php:7.4-apache

USER root
LABEL maintainer="eliab.lemus.barrios@gmail.com"

# Variables de entorno
ENV DEBIAN_FRONTEND=noninteractive
ENV MODULES_PATH=/tmp/rachel_modules

# Crear carpetas necesarias
RUN mkdir -p /tmp/installer /var/modules/bin

# Copiar instaladores personalizados y entrypoint
COPY Installer/ /tmp/installer/
COPY entrypoint.sh /usr/bin/

# Instalar paquetes del sistema y extensiones PHP
RUN apt-get update && apt-get install -y \
    curl \
    net-tools \
    python3 \
    python3-apt \
    python3-dbus \
    python3-psutil \
    python3-pkg-resources \
    sudo \
    tzdata \
    vim \
    wget \
    whiptail \
    dirmngr \
    apt-utils \
    libonig-dev \ 
    && apt-get clean \
    && docker-php-ext-install pdo_mysql mbstring bcmath

# Permisos y archivos especiales
COPY Installer/files/rachel/rachel_sudoers /etc/sudoers.d/rachel
RUN chown root:root /etc/sudoers.d/rachel \
    && chmod 0440 /etc/sudoers.d/rachel \
    && echo '1' > /etc/school-id \
    && chmod +x /usr/bin/entrypoint.sh \
    && chmod +x /tmp/installer/installer.py \
    && chmod +x /tmp/installer/modules/install.py \
    && mv /tmp/installer/modules/install.py /var/modules/bin/.

# Configuración del directorio de trabajo
WORKDIR /var/www/html

# Entrypoint
ENTRYPOINT ["/usr/bin/entrypoint.sh"]
