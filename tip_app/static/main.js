const tipForm = document.getElementById('tip-form')

if (tipForm) {
  tipForm.addEventListener('change', e => {
    e.preventDefault()
    const endpointMatchDay = document.getElementById('matchday-endpoint-url').getAttribute('url');
    const newTipId = e.target.id
    const newTipValue = document.getElementById(e.target.id).value
    const newJoker = document.getElementById(e.target.id).checked
    // console.log(newTipId);
    // console.log(newJoker)
    // console.log(newTipValue)
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
        // console.log("#######e#######")
        // console.log(e)
        // console.log("#######e#######-------")
        for (var i = 0; i < e.match_array_length; i++) {
          let match_id = Object.keys(e.matchday_matches_ids_and_matchdates)[parseInt(i)]
          // console.log(match_has_started(e.matchday_matches_ids_and_matchdates[match_id]))
          if (upperLimitJokersReached(e.m_nr, e.n_joker) || match_has_started(e.matchday_matches_ids_and_matchdates[match_id])) {
            jokerButton = document.getElementById('joker_' + `${match_id}`)
            if (!jokerButton.checked) {
              jokerButton.disabled = true
            }
          }
          else {
            let match_id = Object.keys(e.matchday_matches_ids_and_matchdates)[parseInt(i)]
            jokerButton = document.getElementById('joker_' + `${match_id}`)
            if (!jokerButton.checked) {
              // console.log(jokerButton)
              jokerButton.disabled = false
            }
          }
        }
      }
    });
  })
}

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

function match_has_started(matchdate) {
  var now = new Date().getTime();
  const formatted_matchdate = new Date(matchdate).getTime();
  const distance = formatted_matchdate - now;
  return distance < 0
}

function upperLimitJokersReached(matchday, nJoker) {
  if (matchday < 3 && nJoker == 3) {
    return true;
  }
  if (matchday == 3 && nJoker == 1) {
    return true;
  }
  if (matchday == 4 && nJoker == 1) {
    return true;
  }
  if (matchday > 4 && nJoker == 1) {
    return true;
  }
  return false;
}