# Tech Reviews Website

[View the live website here](http://tech-reviews.herokuapp.com/)

Tech Reviews is a fictitious consumer electronics reviews and consumer advice company based in Manchester, United Kingdom. This is the organisation's main marketing website which aims to inform customers about the different consumer electronics products currently available in the marketplace and persuade them to make a purchase. It provides customers with information and reviews for a variety of products including phones, tablets, laptops, speakers and smart watches. The website is designed to be responsive and easy to navigate on a range of devices.

## User Experience (UX)

### User Stories

1. As a customer or a site owner, I want to be able to navigate the website easily to find the content I am looking for.
2. As a customer, I want to be able to find out about the latest consumer electronics products.
3. As a customer, I want to be able to sign up for email updates about the latest consumer electronics products.
4. As a customer, I want to be able to search for products that meet my needs.
5. As a customer, I want to be able to view product information and read reviews for each product.
6. As a customer, I want to be able to sign in to my account or sign up for an account if I don't already have one. 
7. As a customer, I want to be able to write reviews of products.
8. As a customer, I want to be able to edit and delete my reviews.
9. As a site owner, I want to be able to add, edit and delete products.
10. As a customer, I want to be able to contact the organisation to get answers to any questions I may have.
11. As a customer, I want to be able to find the organisation's social media links.

### Design

#### Colour Scheme

- The three main colours used in the website are black, white, green and grey.
- These colours were chosen because the black/grey contrasts with the green/white.

#### Typography

- The main font used throughout the website is Nunito Sans.
- This font was chosen because it makes the content easy to read.
- Sans Serif is the fallback font which is used in the event that the specified font fails to import into the website correctly.

#### Imagery

- The home page hero image was chosen because it give the user an idea of what kind of products they can find out more about on the site.

- The contact us page hero image was chosen because it adds to the ambiance of the page.

- The product images were chosen because they give the user an idea of what they can expect if they choose to purchase the product.

## Features

### Existing Features

1. Brand Logo

   - This familiarises users with the organisation's logo and is also a link which the user can access from any page to take them back to the home page.

2. Navigation links

   - These enable users to access the different pages of the website so they can easily find the content they are looking for.

3. Search Bar

    - This enables users to search for products by name or brand.

4. Home Page Hero Image

   - This provides users with an image which gives them an idea of the kind of products they can find out about on the site and a link to the sign up page.

5. Featured Products Carousel

   - This provides users with the product's name, an image and a link to the procuct's page for six of the latest products.

6. Newsletter Sign Up

    - This enables users to sign up to receive updates about the latest products by entering their email address into the form.

7. Reviews Search Results / Product Category Reviews

    - This displays all the products that match the search criteria. For each product, it's name, image, overall rating and price is diaplayed. Each product image is a link to the product's page. 
    - Users can sort the products returned by the search by using the sort by dropdown or filter the products by using the filters in the sidebar (the filters form can be accessed by clicking on the filters button on mobile devices).

8. Product Details

    - This provides users with details of the product including colours, price, capacity, display, processor, memory, graphics, camera and video capabilities, battery life and connectivity.

9. Product Ratings

    - This displays progress bars displaying the average ratings from the reviews for overall rating, performace, usability, price, quality. 
    - Progress bars are also displayed for the percentage of users who rated the product each star rating overall.

10. Product Reviews

    - This enables users to read the reviews that other users have written and vote whether each the review is helpful or not.
    - If the user is signed in, they can write their own review for the product and edit or delete their review if they have already written one by clicking on the relevant links.

11. Add/Edit Review Forms

    - These enable users to add or edit the details of their review.

12. Sign Up Form

    This enables users to sign up for an account by entering their first name, last name, email address and password into the form. It also provides them with an opportunity to sign up to the newsletter.

13. Sign In Form

    - This enables users to sign in to their account by entering their email address and password.

14. Account

    - When a user is signed in, this display's all the reviews the user has written and provides them with links to edit and delete each review.

15. Product Management

    - When an admin user is signed in, this display's all the products currently listed on the site, each product's category and links to edit and delete each product. 
    - Admin users can also add a new product by clicking on the add product link or sort the products by selecting an option from the sort by dropdown.

16. Add/Edit Product Forms

    - These enable admin users to add or edit the product's details.

17. Contact Us Form

    - This enables users to contact the organisation about any questions they may have by completing the form. If a user is signed in, their name and email address are automatically entered into the relevant form fields.

18. Footer Navigation links

    - These enable users to access key different pages of the website so they can easily find the content they are looking for.

19. Social Media links

    - These provide users with links to the different social media platforms where the organisation has a presence.

20. Responsive Design

    - Bootstrap grids and CSS media queries are used throughout the website to ensure that it is optimised for use on devices with a wide range of screen sizes.

### Features Left to Implement

1. More Products and Categories

   - Add more products including from additional categories.

2. Add Expert Reviews

    - Add reviews to product details pages written by Subject Matter Experts

3. Add an Offers Page

    - Add an offers page which details the latest offers and provides customers with links to partners' sites where they can purchase the product.

4. One Review Per Product

    - Add functionality to prevent users from being able to write multiple reviews for the same product.

5. Sort Reviews by Ratings or Date Written

    - Add a dropdwon to the product details pages to give users the option to sort the reviews by ratings or date written.

6. 5 More Reviews and Show All Reviews Buttons

    - Add buttons to the product details pages to display 5 more reviews or show all reviews.

## Technologies Used

### Languages Used

1. [HTML5:](https://en.wikipedia.org/wiki/HTML5/)
   - HTML5 was used for the sturcture of the webpages.
2. [CSS3:](https://en.wikipedia.org/wiki/Cascading_Style_Sheets/)
   - CSS3 was used for the styling of the webpages.
3. [JavaScript:](https://en.wikipedia.org/wiki/JavaScript/)
   - JavaScript was used for the interactive features on the webpages.
4. [Python:](https://www.python.org/)
    - Python was used to communicate the database information to the browser.

### Frameworks, Libraries & Programs Used

1. [Bootstrap 4.5](https://getbootstrap.com/)
   - Bootstrap was used for the navbar, footer accordion, toasts, forms, buttons, filters modal, sort by dropdown buttons, featured products carousel cards and reviews cards. Bootstrap was also used for the grid which assists with the responsiveness of the website and for the styling.
2. [Hover.css](https://ianlunn.github.io/Hover/)
   - Hover.css was used for the hover effects on the social media icons.
3. [Font Awesome](https://fontawesome.com/)
   - Font Awesome was used throughout the website to enhance the user experience by adding icons.
4. [Popper.js](https://popper.js.org/)
   - Bootstrap uses Popper.js to make the navbar responsive.
5. [jQuery](https://jquery.com/)
   - JQuery was used throughout the website for the interactive features.
6. [Slick Slider](https://kenwheeler.github.io/slick/)
    - Slick Slider was used for the featured products carousel. License is [here](slick_license.md).
7. [Flask](https://flask.palletsprojects.com/en/1.1.x/)
   - Flask was used for the routing of the appliction and for the messages.
8. [Flask Paginate](https://pythonhosted.org/Flask-paginate/)
   - Flask Paginatie was used for the pagination on the reviews, category reviews and product management pages.
9. [Jinja](https://jinja.palletsprojects.com/en/2.11.x/)
   - Jinja was used for the templating.
10. [Flask-PyMongo](https://flask-pymongo.readthedocs.io/en/latest/)
    - Flask-PyMongo was used to interact with the database. 
11. [MongoDB](https://owlcarousel2.github.io/OwlCarousel2/)
    - A MongoDB database was used to store the data used in the project.
12. [Gitpod](https://www.gitpod.io/)
    - Gitpod was used to write the code for this project and gitpod terminal was used to commit changes to Git and Push them to GitHub.
13. [Git](https://git-scm.com/)
    - Git was the version control system used for this project.
14. [GitHub](https://github.com/)
    - GitHub is used to store the project's code and any other required files.
15. [Heroku](https://www.heroku.com/)
    - Heroku is used to host the deployed website.
16. [Balsamiq](https://balsamiq.com/)
    - Balsamiq was used to create the wireframes during the design phase of the project.

## Testing

### WC3 Validation

The W3C Markup Validator and W3C CSS Validator Services were used to validate every page of the website to ensure that the code used was in compliance with the HTML5 and CSS3 standards and that there were no syntax errors.

- [Home]()
- [Reviews / Category Reviews]()
- [Product Details]()
- [Add Review]()
- [Edit Review]()
- [Register]()
- [Sign In]()
- [Sign Out]()
- [Account]()
- [Product Management]()
- [Add Product]()
- [Edit Product]()
- [403]()
- [404]()
- [CSS]()

### Testing User Stories from User Experience (UX) Section

1. As a customer or a site owner, I want to be able to navigate the website easily to find the content I am looking for.

    - The navigation bar can be easily accessed in the header of each page. 
    - It is clean and easy to read and contains the organisation's logo and the navigation links to the other pages of the website.
    - Each of the navigation links clearly communicates to the user what page it will take them to.
    - The Tech Reviews brand logo is also a link which takes the user back to the home page.
    - The footer also contains key links which take the user to the category reviews pages, contact page and either the account page (standard users) or product management page (admin users) if the user is signed in.
    - The website is structured in a logical way with the hero image, featured products carousel and newsletter sign up on the home page, and each other item of content on it's own page.

2. As a customer, I want to be able to find out about the latest consumer electronics products.

    - The featured products carousel is clearly highlighted on the home page.
    - This contains information about the latest products including an image of each product which links to it's page, and it's name. Users can find out more about the product, view it's ratings and read user reviews on the product's page.

3. As a customer, I want to be able to sign up for email updates about the latest consumer electronics products.

    - The newsletter sign up section is clearly highlighted on the home page.
    - This contains a form where users can enter their email address to sign up to receive email updates about the latest products.

4. As a customer, I want to be able to search for products that meet my needs.

    - The search bar is clearly highlighted in the navigation bar in the header of each page. Here users can enter a product name or brand to search for products.
    - The reviews dropdown is clearly highlighted in the navigation bar in the header of each page. Here users can select a product category which will search for all of the products in the category.
    - Users can sort the products by selecting an option from the sort by dropdown.
    - Users can further refine their search by selecting options from the filters form in the sidebar. On mobile devices, users can access the filters form by clicking on the filters button.
    - For each product that satisfies the user's search criteria, an image of the product which links to it's page, it's name, it's price and it's average user rating is displayed.

5. As a customer, I want to be able to view product information and read reviews for each product.

    - Users can access a product's page by clicking on a product image on the reviews search results or category reviews pages.
    - Here the user can find information about the product including it's colours, price, capacity, display, processor, memory, graphics, camera and video capabilities, battery life and connectivity.
    - They can also view the product's average ratings for performace, usability, price and quality, and the percentage of users who rated the product each star rating overall.
    - User reviews are also available for the users to read and rate whether they were helpful or not on the product page.

6. As a customer, I want to be able to sign in to my account or sign up for an account if I don't already have one. 

    - Users can access the sign in / register links by clicking on the user dropdown (large screens and above) or by clicking on the relevant links in the navigation bar (small and medium screens). There are also links to the sign in / register pages in the footer.
    - On the sign in page, users can sign in to their account.
    - On the register page, users can sign up for an account if they haven't already registered for one.

7. As a customer, I want to be able to write reviews of products.

    - The add review link is clearly highlighted on the product pages when the user is signed in.
    - If the user clicks on this link, they are taken to the add review form which they can complete to add a review for the product.

8. As a customer, I want to be able to easily access my reviews to edit and delete them.

    - Users can access their reviews by clicking on the user dropdown and selecting the account option (large screens and above) or by clicking on the account link in the navigation bar (small and medium screens). There is also a link to the account page in the footer.
    - Here, users can find cards for all of the reviews they have written which include links to the edit and delete the review. 
    - Users can also find links to edit and delete their reviews in the review card on the relevant product page.
    - When a user clicks on the edit link, they are taken to the edit review form where they can amend the details of their review.
    - When a user clicks on the edit link, their review is deleted.

9. As a site owner, I want to be able to add, edit and delete products.

    - Site owners can access the product management page by clicking on the user dropdown and selecting the product management (large screens and above) or by clicking on the product management link in the navigation bar (small and medium screens). There is also a link to the product management page in the footer.
    - Here, site owners can find a table containing all of the products that are currently listed on the site. Each product's row displays the product's name, category, and links to the edit and delete the product. 
    - When a site owner clicks on the edit link, they are taken to the edit product form where they can amend the relevant product details.
    - When a site owner clicks on the delete link, the product is deleted.
    - Site owners can can add a new product by clicking on the add product link which takes them to the add product form.

10. As a customer, I want to be able to contact the organisation to get answers to any questions I may have.

    - A link to the contact us page is clearly highlighted in the navigation bar and in the footer.
    - Here there is a form which the user can complete to get in touch with the organisation.

11. As a customer, I want to be able to find the organisation's social media links.

    - The social media icons are clearly highlighted in the footer of each page.
    - Each of these provides a link to the relevant social media platform.

### Manual Testing

Details of the manual testing carried out can be viewed [here]().

### Further Testing

- The Website was tested on a variety of different web browsers including Google Chrome, Microsoft Edge, Safari and Firefox.
- The Website was also viewed on a number of different devices with a range of screen widths including an iMac, MacBook, iPad and iPhone.
- Family and friends were asked to review the site and documentation and identify any bugs or other issues that were affecting the user experience.

## Deployment

### Heroku

The project was deployed to Heroku using the following steps:

1.  Log in to Heroku and click on the "New" button.
    ![Image showing the new button](static/images/deployment/deployment1.png)
2.  Click on the "Create new app" button in the dropdown list.
    ![Image showing the create new app button in the dropdown list](static/images/deployment/deployment2.png)
3.  Enter a name for the app and check that it is available.
    ![Image showing the create app form](static/images/deployment/deployment3.png)
4.  Click the "Create app" button.
    ![Image showing the create app button](static/images/deployment/deployment4.png)
5.  Scroll down to the connect to GitHub section, enter the project's GitHub repository name in the repo-name field and click the "Search" button.
    ![Image showing the connect to GitHub section](static/images/deployment/deployment5.png)
6.  Click the "Connect" button next to the GitHub repository.
    ![Image showing the connect button](static/images/deployment/deployment6.png)
7.  Scroll down to the automatic deploys section and click the "Enable Automatic Deploys" button.
    ![Image showing the enable automatic deploys section](static/images/deployment/deployment7.png)
8.  Scroll back up to the top of the page and click the "Settings" tab.
    ![Image showing the settings tab](static/images/deployment/deployment8.png)
9.  Scroll down to the convig vars section and click the "Reveal Config Vars" button.
    ![Image showing the reveal config vars button](static/images/deployment/deployment9.png)
10. Enter the key and value for each config var and click the "add" button.
    ![Image showing the config vars input form](static/images/deployment/deployment10.png)

More information about deploying a website to Heroku is available [here](https://devcenter.heroku.com/categories/deployment).

### Forking the GitHub repository

The GitHub Repository can be forked using the following steps:

1.  Log in to GitHub and locate the project's [GitHub Repository](https://github.com/jonathan-odonnell/milestone-project-3).
2.  At the top-right of the repository, click the "Fork" Button.
    ![Image showing the fork button](static/images/fork/fork.png)

More information about forking a GitHub repository is available [here](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo).

### Making a Local Clone

A local clone of the project can be created using the following steps:

1.  Log in to GitHub and locate the project's [GitHub Repository](https://github.com/jonathan-odonnell/milestone-project-3).
2.  Under the repository name, click the "Code" button.
    ![Image showing the code button](static/images/clone/clone1.png)
3.  To clone the repository using HTTPS, under "Clone with HTTPS", click the clipboard button to copy the repository URL.
    ![Image showing the clipboard button](static/images/clone/clone2.png)
    To clone using SSH click "Use SSH" and then click the clipboard button.
    ![Image showing the use ssh button](static/images/clone/clone3.png)
    ![Image showing the clipboard button](static/images/clone/clone4.png)
4.  Open Git Bash
5.  Change the current working directory to the location where you want to store the cloned repository.
6.  Type `git clone` and then paste the URL you copied in Step 3.

```
$ git clone https://github.com/jonathan-odonnell/milestone-project-3.git
```

7.  Press enter to create your clone.

```
Cloning into 'milestone-project-3'...
remote: Enumerating objects: 1900, done.
remote: Total 1900 (delta 0), reused 0 (delta 0), pack-reused 1900
Receiving objects: 100% (1900/1900), 74.54 MiB | 4.68 MiB/s, done.
Resolving deltas: 100% (1290/1290), done.
```

More information about making a local clone of a GitHub repository is available [here](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository).