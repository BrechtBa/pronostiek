<?php

///////////////////////////////////////////////////////////////////////////////
// Display Progress
///////////////////////////////////////////////////////////////////////////////
// There are 2 progress versions all handled by this file
// prono:  used to fill in the guess of all users: $enabled = 1
// disp:   used to show the user guesses         : $enabled = 0

$enabled_str = "";

if($enabled){
	// prono
}
else{
	// disp
	$enabled_str = "disabled";
}

// get user data
$query  = "SELECT * FROM wk_users WHERE id='$userid'";
$result = mysql_query($query) or die('Error: ' . mysql_error());
$row = mysql_fetch_array($result);
	
echo "
					<div class=ko1>
						<h1>Ploegen in de Kwartfinales:</h1>";	
						echo_select_list("quarter_team1",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["quarter_team1"]);
						echo_select_list("quarter_team2",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["quarter_team2"]);
						echo_select_list("quarter_team3",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["quarter_team3"]);
						echo_select_list("quarter_team4",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["quarter_team4"]);
						echo_select_list("quarter_team5",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["quarter_team5"]);
						echo_select_list("quarter_team6",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["quarter_team5"]);
						echo_select_list("quarter_team7",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["quarter_team6"]);
						echo_select_list("quarter_team8",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["quarter_team7"]);
						
echo "     
					</div>
					<div class=ko1>
						<h1>Ploegen in de Halve finales:</h1>";	
						echo_select_list("semi_team1",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["semi_team1"]);
						echo_select_list("semi_team2",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["semi_team2"]);
						echo_select_list("semi_team3",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["semi_team3"]);
						echo_select_list("semi_team4",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["semi_team4"]);

echo "     
					</div>
					<div class=ko1>
						<h1>Ploegen in de Finale:</h1>";
						echo_select_list("final_team1",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["final_team1"]);
						echo_select_list("final_team2",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["final_team2"]);
						
echo "     
					</div>
					<div class=ko1>
						<h1>Wereldkampioen:</h1>";
						echo_select_list("winner",$enabled,array_merge((array)"",$team_name),array_merge((array)-1,range(1,count($team_name))),$row["winner"]);
						
echo "     
					</div>";
					
?>