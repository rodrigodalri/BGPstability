#!/bin/bash

if [ $# -lt 4 ];
  then
   echo "route_collector year month day"
   exit 1
fi

  #route_collector example = route-collector.decix-ham.fra.pch.net
  route_collector=$1
  year=$2
  month=$3
  day=$4

  echo "Download MRT Files PCH - $route_collector from $year/$month/$day"

  for k in {0..9};
    do
      for i in {0..9};
      do
        echo "Downloading 0$k:0$i"
        wget https://www.pch.net/resources/Raw_Routing_Data/$route_collector/$year/$month/$day/$route_collector-mrt-bgp-updates-$year-$month-$day-0$k-0$i.gz
      done
    done

  for k in {10..23};
    do
      for i in {0..9};
      do
        echo "Downloading $k:0$i"
        wget https://www.pch.net/resources/Raw_Routing_Data/$route_collector/$year/$month/$day/$route_collector-mrt-bgp-updates-$year-$month-$day-$k-0$i.gz
      done
    done

  for k in {0..9};
    do
      for i in {10..59};
      do
        echo "Downloading 0$k:$i"
        wget https://www.pch.net/resources/Raw_Routing_Data/$route_collector/$year/$month/$day/$route_collector-mrt-bgp-updates-$year-$month-$day-0$k-$i.gz
      done
    done

  for k in {10..23};
    do
      for i in {10..59};
      do
        echo "Downloading $k:$i"
        wget https://www.pch.net/resources/Raw_Routing_Data/$route_collector/$year/$month/$day/$route_collector-mrt-bgp-updates-$year-$month-$day-$k-$i.gz
      done
    done
