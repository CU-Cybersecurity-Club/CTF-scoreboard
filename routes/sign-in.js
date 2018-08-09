const express = require('express');
const router  = express.Router();

// GET sign-in/sign-up page
router.get('/', function(req, res, next) {
	res.render('sign-in', { title: 'CU Cybersecurity' });
});

module.exports = router;
