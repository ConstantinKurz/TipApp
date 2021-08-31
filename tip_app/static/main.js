const tipForm = document.getElementById('tip-form')

if (tipForm) {
  tipForm.addEventListener('change', e => {
    e.preventDefault()
    const endpointMatchDay = document.getElementById('matchday-endpoint-url').getAttribute('url');
    const newTipId = e.target.id
    const newTipValue = document.getElementById(e.target.id).value
    const newJoker = document.getElementById(e.target.id).checked
    console.log(newTipId);
    console.log(newJoker)
    console.log(newTipValue)
    $.ajaxSetup({
      headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
      }
    });
    $.ajax({
      url: endpointMatchDay,
      method: 'POST',
      data: JSON.stringify({
        'tip_id': newTipId,
        'tip_value': newTipValue,
        'joker': newJoker
      }),
      dataType: 'json',
      processData: false,
      contentType: false,
      success: function (e) {
        console.log(e)
        console.log(e.n_joker)
        console.log(e.matchday_matches_ids)
        var matchIdArray = e.matchday_matches_ids;
        var matchIdArrayLength = matchIdArray.length;
        if (upperLimitJokersReached(e.m_nr, e.n_joker)) {
          console.log('too many')
          for (var i = 0; i < matchIdArrayLength; i++) {
            console.log(matchIdArray[i])
            console.log(document.getElementById('joker_' + `${matchIdArray[i]}`))
            jokerButton = document.getElementById('joker_' + `${matchIdArray[i]}`)
            console.log(jokerButton)
            if (!jokerButton.checked) {
              jokerButton.disabled = true
            }
          }
          console.log("++++++++")
        }
        else {
          for (var i = 0; i < matchIdArrayLength; i++) {
            jokerButton = document.getElementById('joker_' + `${matchIdArray[i]}`)
            if (!jokerButton.checked) {
              console.log(jokerButton)
              jokerButton.disabled = false
            }
          }
        }
      },
      error: function (e) {
        // alert('Zu viele Joker gesetzt' + e)
      }
    })
  });
};

const home_endpoint = document.getElementById('home-endpoint-url');
if (home_endpoint) {
  const url = home_endpoint.url;
  const x = setInterval(function () {
    $.ajaxSetup({
      headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
      }
    });
    $.ajax({
      url: url,
      method: 'GET',
      success:
        function (response) {
          var now = new Date().getTime();
          const countDownDate = new Date(response.upcoming_match_time).getTime();
          const distance = countDownDate - now;

          // Time calculations for days, hours, minutes and seconds
          const days = Math.floor(distance / (1000 * 60 * 60 * 24));
          const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
          const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((distance % (1000 * 60)) / 1000);
          const count_days = document.getElementById('days');
          const count_hours = document.getElementById('hours');
          const count_minutes = document.getElementById('minutes');
          const count_seconds = document.getElementById('seconds');

          count_days.innerHTML = days;
          count_hours.innerHTML = hours;
          count_minutes.innerHTML = minutes
          count_seconds.innerHTML = seconds;

          if (distance <= 0) {
            clearInterval(x)
          }
        },
    });
  }, 1000)
}

function upperLimitJokersReached(matchday, nJoker) {
  if (matchday < 3 && nJoker == 3) {
    return true;
  }
  if (matchday == 4 && nJoker == 1) {
    return true;
  }
  if (matchday == 5 && nJoker == 1) {
    return true;
  }
  if (matchday > 5 && nJoker == 2) {
    return true;
  }
  return false;
}