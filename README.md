<h1 align="center">The Medialist</h1>
<p align="center">
  <img alt="the medialist logo" width="200" height="200" src="staticfiles/images/earth.png">
</p>

The backend code for The Medialist written in pure Python.

The Medialist is an open source news website that provides news in its most unfiltered form. It also aggregates news articles from all over the Internet and rates them on their objectivity. This project exists due to the clear as day bias that haunts almost every newspaper out there right now - be it Fox News or the Washington Times.

The rating is for each article is calculated by a machine learning model between 0 and 1 - with 0 being extremely subjective with a lot of bias and 1 implying the post to be very objective. A ranking of 0.5 and less classifies the article as subjective and vice versa. The entire backend code (along with the neural networks) is written in Python. The web backend is just a RESTful API written using Django (and django-rest-framework).

The frontend is being written in React. Note - this project is far from ready. But documentation and contribution guides will be coming soon. Until then, feel free to look around and familiarize yourself.
