<?php
    # for multi-lingual support
    require_once($_SERVER['DOCUMENT_ROOT'] . "/admin/common.php");
?>
<!DOCTYPE html>
<html lang="<?php echo $lang['langcode'] ?>">
<head>
    <meta charset="utf-8">
    <title>RACHEL</title>
    <style type="text/css">
        body {
          background:#ccc;
          font-family: sans-serif;
          width: 600px;
          margin: 0 auto;
          text-align: center;
	  color:#666;
        }
        h2 { margin: 40px; }
        #btn {
	  display:inline-block;
	  height:26px;
	  width:138px;
          background: #2abfd8;
          color: #fff;
          padding: 8px;
          border-radius: 4px;
          text-decoration: none;
        }
        #btn:hover {
            background: #32cce6;
        }

		#container {
			position: absolute;
            top: 50%;
            margin-top: -200px;
            /* half of #content height*/
            left: 0;
            width: 100%;
        }

		#content {
			width: 624px;
            margin-left: auto;
            margin-right: auto;
            height: 395px;
		}

    </style>
</head>
<body>
  <div id="container">
    <div id="content">
    <h1><a href="http://<?php echo $_SERVER["SERVER_ADDR"]; ?>/index.php" target="_blank"><img src="http://<?php echo $_SERVER["SERVER_ADDR"]; ?>/art/logo.png" width="117" height="146"></a></h1>


    <h3>500: Internal server error</h3>

    <h2><a href="http://<?php echo $_SERVER["SERVER_ADDR"]; ?>/index.php" id="btn">RACHEL</a></h2>
    </div>
  </div>
</body>
</html>
