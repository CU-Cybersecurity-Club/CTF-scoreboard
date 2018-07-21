var express = require('express');
var router  = express.Router();

// GET leaderboard page
router.get('/', function(req, res, next) {
	console.log( 'getting the leaderboard page...' );
	res.render('leaderboards', {title: 'Leaderboards'});
});

module.exports = router;
