# Use the official amazonlinux AMI image
FROM public.ecr.aws/lambda/python:3.8

COPY app ${LAMBDA_TASK_ROOT}/app

# Install apt dependencies
RUN yum install -y gcc gcc-c++ freetype-devel yum-utils findutils openssl-devel 
RUN yum install -y libjpeg-devel gdal-bin libgdal-dev libffi-devel fast
RUN yum install -y automake16 libpng-devel nasm libxml2-devel readline-devel curl-devel cmake3
RUN yum -y groupinstall development

ENV PREFIX=/usr/local

ENV \
  HDF5_VERSION=1.12.0 \
  NETCDF_VERSION=4.7.4 \
  PYTHON_VERSION=3.8.2

ENV LD_LIBRARY_PATH=$PREFIX/lib:$PREFIX/lib64:$LD_LIBRARY_PATH
ENV PATH=$PREFIX/bin/:$PATH

# libhdf5
RUN mkdir /tmp/hdf5 \
  && curl -sfL https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-${HDF5_VERSION%.*}/hdf5-${HDF5_VERSION}/src/hdf5-$HDF5_VERSION.tar.gz | tar zxf - -C /tmp/hdf5 --strip-components=1 \
  && cd /tmp/hdf5 \
  && CFLAGS="-O2 -Wl,-S" CXXFLAGS="-O2 -Wl,-S" ./configure \
  --prefix=$PREFIX \
  --with-szlib=$PREFIX \
  --enable-cxx \
  --enable-thread-safe \
  --disable-static \
  && make -j $(nproc) --silent && make install && make clean \
  && rm -rf /tmp/hdf5

# netcdf
RUN mkdir /tmp/netcdf \
  && curl -sfL https://github.com/Unidata/netcdf-c/archive/v$NETCDF_VERSION.tar.gz | tar zxf - -C /tmp/netcdf --strip-components=1 \
  && cd /tmp/netcdf \
  && CFLAGS="-O2 -Wl,-S" CXXFLAGS="-O2 -Wl,-S" CPPFLAGS="-I$PREFIX/include" LDFLAGS="-L$PREFIX/lib" ./configure \
  --with-default-chunk-size=67108864 \
  --with-chunk-cache-size=67108864 \
  --prefix=$PREFIX \
  --disable-static \
  --enable-netcdf4 \
  --enable-dap \
  --with-pic \
  && make -j $(nproc) --silent && make install && make clean \
  && rm -rf /tmp/netcdf

# Install Python dependencies
RUN pip3 install lambda-proxy==5.2.1
RUN pip3 install numpy --no-binary numpy
RUN pip3 install sat-search==0.3.0
RUN pip3 install pyproj==1.9.6 rasterio
RUN pip3 install intake-stac
RUN pip3 install shapely==1.7.1
RUN pip3 install --no-cache-dir scipy

CMD ["app.handler.handle"]
