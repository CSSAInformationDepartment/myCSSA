<?php	
	if(empty($_POST['name_23730']) && strlen($_POST['name_23730']) == 0 || empty($_POST['email_23730']) && strlen($_POST['email_23730']) == 0 || empty($_POST['message_23730']) && strlen($_POST['message_23730']) == 0)
	{
		return false;
	}
	
	$name_23730 = $_POST['name_23730'];
	$email_23730 = $_POST['email_23730'];
	$message_23730 = $_POST['message_23730'];
	$optin_23730 = $_POST['optin_23730'];
	
	$to = 'receiver@yoursite.com'; // Email submissions are sent to this email

	// Create email	
	$email_subject = "Message from a Blocs website.";
	$email_body = "You have received a new message. \n\n".
				  "Name_23730: $name_23730 \nEmail_23730: $email_23730 \nMessage_23730: $message_23730 \nOptin_23730: $optin_23730 \n";
	$headers = "MIME-Version: 1.0\r\nContent-type: text/plain; charset=UTF-8\r\n";	
	$headers .= "From: contact@yoursite.com\n";
	$headers .= "Reply-To: $email_23730";	
	
	mail($to,$email_subject,$email_body,$headers); // Post message
	return true;			
?>