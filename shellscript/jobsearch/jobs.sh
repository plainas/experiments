#!/bin/bash

# Requirements: fzf, jq

if  [ $# -eq 2 ] && [ $2 = "pick_job" ] ; then
    v_job_id=$(echo $1 | awk '{print $1;}')
    V_JOB_DESCRIPTION=$(jq -r '.hits[]  | select(.id=="'$v_job_id'") | .description.text' jobsbuffer.json)
    V_PUBDATE=$(jq -r '.hits[]  | select(.id=="'$v_job_id'") | .publication_date' jobsbuffer.json)
    V_DEADLINE=$(jq -r '.hits[]  | select(.id=="'$v_job_id'") | .application_deadline' jobsbuffer.json)
    V_WEBPAGE_URL=$(jq -r '.hits[]  | select(.id=="'$v_job_id'") | .webpage_url' jobsbuffer.json)
    V_EXTERNAL_URL=$(jq -r '.hits[]  | select(.id=="'$v_job_id'") | .application_details.url' jobsbuffer.json)

    V_LOCATION=$(jq -r '.hits[]  | select(.id=="'$v_job_id'") | .workplace_address.city' jobsbuffer.json)
    V_COMPANY=$(jq -r '.hits[]  | select(.id=="'$v_job_id'") | .employer.name' jobsbuffer.json)
    V_POSITION=$(jq -r '.hits[]  | select(.id=="'$v_job_id'") | .headline' jobsbuffer.json)

    green=$(tput setaf 2)
    normal=$(tput sgr0)
    printf "${green}POSITION:${normal} %s \n" "$V_POSITION"
    printf "${green}COMPANY:${normal} %s \n" "$V_COMPANY"
    printf "${green}LOCATION:${normal} %s \n" "$V_LOCATION"
    printf "${green}PUBLISHED:${normal} %s \n" "$V_PUBDATE"
    printf "${green}APPLICATION DEADLINE:${normal} %s\n\n" "$V_DEADLINE"
    printf "${green}DESCRIPTION:${normal}\n%s" "$V_JOB_DESCRIPTION" | fmt
    printf "${green}Link:${normal} %s \n" "$V_WEBPAGE_URL"
    printf "${green}External link:${normal} %s \n" "$V_EXTERNAL_URL"
    exit
fi


f_http_search_jobs(){
    curl "https://jobsearch.api.jobtechdev.se/search?q=$1&offset=0&limit=100" \
    -H 'accept: application/json' 
}


v_urlencoded_q="${1// /+}"

v_jobs_json_str=$(f_http_search_jobs $v_urlencoded_q)

printf '%s' "$v_jobs_json_str" > jobsbuffer.json

printf '%s' "$v_jobs_json_str" \
    | jq -r '.hits[] | (.id +" [\u001b[33m"+ .employer.name +"\u001b[0m] "+ .headline)'  \
    | fzf --layout=reverse --ansi --preview "'${BASH_SOURCE[0]}' {} pick_job"
