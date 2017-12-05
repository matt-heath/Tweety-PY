<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tweety-Py</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" integrity="sha256-eZrrJcwDc/3uDhsdt61sL2oOBY362qM3lon1gyExkL0=" crossorigin="anonymous" />
  <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,400,700" rel="stylesheet">
  <!-- Bulma Version 0.6.0 -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.6.0/css/bulma.min.css" integrity="sha256-HEtF7HLJZSC3Le1HcsWbz1hDYFPZCqDhZa9QsCgVUdw=" crossorigin="anonymous" />

  <style>

    html,body {
        font-family: 'Open Sans', serif;
        background: #F2F6FA;
    }
    footer {
      background-color: #F2F6FA !important;
    }
    .topNav {
      border-top: 5px solid #3498DB;
    }
    .topNav .container {
      border-bottom: 1px solid #E6EAEE;
    }
    .container .columns {
      margin: 3rem 0;
    }
    .navbar-menu .navbar-item {
      padding: 0 2rem;
    }
    aside.menu {
      padding-top: 3rem;
    }
    aside.menu .menu-list {
      line-height: 1.5;
    }
    aside.menu .menu-label {
      padding-left: 10px;
      font-weight: 700;
    }
    .button.is-primary.is-alt {
      background: #00c6ff;
      background: -webkit-linear-gradient(to bottom, #0072ff, #00c6ff);
      background: linear-gradient(to bottom, #0072ff, #00c6ff);
      font-weight: 700;
      font-size: 14px;
      height: 3rem;
      line-height: 2.8;
    }
    .media-left img {
      border-radius: 50%;
    }
    .media-content p {
      font-size: 14px;
      line-height: 2.3;
      font-weight: 700;
      color: #8F99A3;
    }
    article.post {
      margin: 1rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid #E6EAEE;
    }
    article.post:last-child {
        padding-bottom: 0;
        border-bottom: none;
    }
  </style>

</head>
<body>

  <nav class="navbar is-white topNav">
    <div class="container">
      <div class="navbar-brand">
        <a class="navbar-item" href="/">
          <b>Tweety-PY</b>
        </a>
      </div>
      <div id="topNav" class="navbar-menu">
        <div class="navbar-start">
          <a class="navbar-item" href="/">
            Home
          </a>
        </div>

        <div class="navbar-end">
            <div class="navbar-item">
                <form method='post' action='/searchTwitter'>
                    <div class="control">
                        <input class="input" type="text" name='searchTwitter' placeholder="Search Twitter">
                    </div>
                </form>
            </div>
            <div class="navbar-item">
                <a href="/logout">
                    Logout
                </a>
            </div>
        </div>
      </div>
    </div>
  </nav>
  <section class="container">
    <div class="columns">
      <div class="column is-3">
          <ul class="menu-list">
            {{!menu}}
          </ul>
        </aside>
      </div>

      <div class="column is-9">
        <div class="card">
            <header class="card-header">
                {{!heading}}
            </header>
            <div class="card-content">
                {{!html}}
            </div>
        </div>
      </div>
    </div>
  </section>
</body>
</html>
