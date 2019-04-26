# SlackMentorBot
Quick and dirty example of slack bot running on GCP Cloud Functions and Firestore to ping people on keywords

# Starting on slack
1. Add app to workspace using my private link
2. Add app to mentor channel
3. Ask mentors to message bot "help" to get started!

# Issues
Due to the slack events API's retry behavior, not replying within 3 seconds means that they will automatically retry and send a second request. 

With cold starts, this can cause issues due to the delay involved in starting a new instance. See https://mikhail.io/2018/08/serverless-cold-start-war/ for why this problem is potentially worse on GCP in particular.

This could be fixed easily if it was not on a FaaS, ironically, as being able to return a response without stopping execution means threads would likely die before they finish. This could be fixed by forwarding the slack request to another function and having the function that simply listens for slack return a 200 response immediately, but that would make this a bit too complex.

The database updates themselves are idempotent, there can be a rare case where issues happen if two instances of this are setting the same new word for two people at once and both enter the section where the update fails because there is no existing record, so both individually set their own one ID arrays into the document. To fix this, I would likely have to add transactions to the individual parts documented here: 
https://firebase.google.com/docs/firestore/manage-data/transactions#transactions
