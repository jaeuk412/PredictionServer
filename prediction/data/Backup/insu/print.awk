#!/usr/bin/awk -f
BEGIN{}
{
	if ($1 == 2019)
		printf "%d %02d %02d %d\n", $1, $2, $3, $4;

}END{}
