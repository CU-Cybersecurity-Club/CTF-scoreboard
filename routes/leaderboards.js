var express = require('express');
var router  = express.Router();

// GET leaderboard page
router.get('/', function(req, res, next) {
	res.render('leaderboards', {title: 'Leaderboards'});
});

module.exports = router;
