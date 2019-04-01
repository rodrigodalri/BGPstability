#!/bin/bash

if [ $# -lt 4 ];
  then
   echo "route_collector year month day"
   exit 1
fi

  #route-collector.decix-ham.fra.pch.net
  route_collector=$1
  year=$2
  month=$3
  day=$4
  outputfile=$5

echo "Parser MRT Files PCH - $route_collector from $year/$month/$day"

  for k in {0..9};
    do
      for i in {0..9};
      do
        echo "Parsing 0$k:0$i"
        python routes_new.py data/$route_collector-mrt-bgp-updates-$year-$month-$day-0$k-0$i $outputfile
      done
    done

  for k in {10..23};
    do
      for i in {0..9};
      do
        echo "Parsing $k:0$i"
        python routes_new.py data/$route_collector-mrt-bgp-updates-$year-$month-$day-$k-0$i $outputfile
      done
    done

  for k in {0..9};
    do
      for i in {10..59};
      do
        echo "Parsing 0$k:$i"
        python routes_new.py data/$route_collector-mrt-bgp-updates-$year-$month-$day-0$k-$i $outputfile
      done
    done

  for k in {10..23};
    do
      for i in {10..59};
      do
        echo "Parsing $k:$i"
        python routes_new.py data/$route_collector-mrt-bgp-updates-$year-$month-$day-$k-$i $outputfile
      done
    done
