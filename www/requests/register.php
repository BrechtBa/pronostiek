<?php
	session_start();
	include('../config/mysql.php');


	$status = 0;
	$user = 0;

	
	if( isset($_POST['username']) && isset($_POST['password']) && isset($_POST['password2']) ){
		// check if the username exists
		$username = $_POST['username'];

		// select the user from the table
		$query = "SELECT id FROM users WHERE username='$username'";
		$result = mysql_query($query) or die('Error: ' . mysql_error());

		if( mysql_num_rows($result) == 0 ){
			// check if the 2 passwords are equal
			if( $_POST['password']==$_POST['password2'] ){

				// check if there are users in the database, else give a privelegde of 1
				$query = "SELECT id FROM users";
				$result = mysql_query($query) or die('Error: ' . mysql_error());
				if( mysql_num_rows($result) == 0 ){
					$priveledge = 9;
				}
				else{
					$priveledge = 1;
				}

				$hashpassword = base64_encode(hash(HASH_ALGORITHM, $_POST['password'], true));
				$query = "INSERT INTO users (username,password,priveledge) VALUES ('$username','$hashpassword','$priveledge')";	
				$result = mysql_query($query) or die('Error: ' . mysql_error());
				$status = 1;
			}
			else{
				$status = -1;
			}
		}
		else{
			$status = -2;
		}
	}
	echo json_encode( array('status' => $status, 'user' => $user) );

?>
