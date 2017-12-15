#!/bin/bash

scriptname=$0
graphgen=$1
CLgraphfile=$2
IterGurobiSolver=$3
NativeGurobiSolver=$4
numberSolutions=$5

if [[ $# -lt 5 ]] #if the number of args less than 5
  then
    echo "usage: project.sh graphgen.py CLgraphfile.py IterGurobiSolver.py NativeGurobiSolver.py numberSolutions"
    exit 1
fi

argumentsArray=( $@ ) #all the command line arguments
#printf '%s ' "${argumentsArray[@]}"
#printf '\n'
lenArgs=${#argumentsArray[@]}
#echo "$lenArgs"
lastElement=${argumentsArray[$lenArgs-1]}
#echo "$lastElement"
argsArWoLast=${argumentsArray[@]:0:$(($lenArgs-1))}
#printf '%s ' "${argsArWOlast[@]}"
#printf '\n'

for i in $argsArWoLast; do #for all the inputted command line args
#printf '%s' "$i"
#printf '\n'
  if [[ ! -e "$i" ]] # if it's not equal to a file
  then
    #echo "Here $i"
    echo "usage: project.sh graphgen.py CLgraphfile.py IterGurobiSolver.py NativeGurobiSolver.py numberSolutions"
    exit 1
  fi
done

if [[ ! $numberSolutions -gt 0 ]]
then
    echo "The number of solutions needs to be greater than 0 and a number!"
    echo "usage: project.sh graphgen.py CLgraphfile.py IterGurobiSolver.py NativeGurobiSolver.py numberSolutions"
    exit 1
fi

#probability 0.50
myFolder="mkdir -vp Test1"
#echo $myFolder
if eval $myFolder ; then
  echo "$myFolder"
else
  echo "$myFolder didn't work"
fi

NodeAmtArray=("200")
for i in $NodeAmtArray ; do
  var="python $graphgen $i 0.50 ${i}graph0.50.txt"
#echo "This is var $var"
  eval $var
done

#mvCom="mv -iv *.txt Test1"
#echo $mvCom
#eval $mvCom

for i in *0.50.txt ; do
  if test -f "$i"
  then
#echo ${i%.txt}
    vari="python $CLgraphfile $i ${i%.txt}.lp"
    eval $vari
  fi
done

timeCmd="touch ItertimeResults${numberSolutions}.txt"
eval $timeCmd

for i in *0.50.lp ; do
  if test -f "$i"
  then
#echo "$i"
    v="python $IterGurobiSolver -r ${i%.lp}.result -n $numberSolutions $i | tail -1 | awk '{ print $3 }' >> ItertimeResults${numberSolutions}.txt"
#echo $v
    eval $v
    who="echo ${i%.lp} Number of Solutions:$numberSolutions >> ItertimeResults${numberSolutions}.txt"
    eval $who
    space="echo "" >> ItertimeResults${numberSolutions}.txt"
    eval $space
  fi
done

timeCmd="touch NativeResults${numberSolutions}.txt"
eval $timeCmd

for i in *0.50.lp ; do
  if test -f "$i"
  then
#echo "$i"
    v="python $NativeGurobiSolver -r ${i%.lp}.result -n $numberSolutions $i | tail -1 >> NativeResults${numberSolutions}.txt"
#echo $v
    eval $v
    who="echo ${i%.lp} Number of Solutions:$numberSolutions >> NativeResults${numberSolutions}.txt"
    eval $who
    space="echo "" >> NativeResults${numberSolutions}.txt"
    eval $space
  fi
done

move="mv NativeResults*.txt Test1"
move1="mv ItertimeResults*.txt Test1"
move2="mv *.lp Test1"
move3="mv *.txt Test1"
move4="mv *.result Test1"
eval $move
eval $move1
eval $move2
eval $move3
eval $move4
