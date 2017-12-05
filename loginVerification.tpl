<html>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Tweety-Py</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.6.0/css/bulma.min.css">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
    <style type="text/css">
      html, body {
        background-color: #eee;
      }
    </style>
</head>

<nav class="navbar is-transparent" style="border-bottom: 2px solid #1DA1F2 ">
      <div class="navbar-brand">
        <a class="navbar-item" href="#">
          <b>Tweety-PY</b>
        </a>
      </div>
    </nav>

    <div class="container column is-half is-offset-one-quarter">
      <div class="card">
        <div class="card-content">
          <p class="title has-text-centered">
            {{message}}
          </p>
          <hr>
          <div class="columns is-centered">
            <div class="field"><br><a href="{{link}}" class="button is-info is-outlined">{{linkMessage}}</a></div>
          </div>
        </div>
      </div>
    </div>

    <!-- jQuery & Javascript -->
    <!-- External JS -->
    <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/limonte-sweetalert2/6.10.1/sweetalert2.min.js"></script>

    <!-- Memo-related JS -->
  </body>
</html>
