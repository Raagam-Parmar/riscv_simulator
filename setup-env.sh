#################################################################
# Sets up the SHELL to run riscv and spike based CA lab course  #
# Assumes following are present in SCRIPTPATH:                  #
#   1. riscv-tools/ appropriate for the Linux distribution      #
#   2. spike/ (a compressed copy is available in dist/)         #
#################################################################


# https://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

RISCV=$SCRIPTPATH/riscv-tools
export PATH="$RISCV/bin:$PATH"
export LIBRARY_PATH="$RISCV/lib"
export LD_LIBRARY_PATH="$RISCV/lib:$LD_LIBRARY_PATH"
export C_INCLUDE_PATH="$RISCV/include"
export CPLUS_INCLUDE_PATH="$RISCV/include"



export PATH="$SCRIPTPATH/spike/bin:$PATH"
export LD_LIBRARY_PATH="$SCRIPTPATH/spike/lib:$LD_LIBRARY_PATH"

