from datetime import date
from django.shortcuts import render
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response


# Create your views here.
@api_view(['GET'])
def get_metrics(request):
    completed_percentage = year_percentage()
    weather_cleaned_data = weather()
    leetcode_cleaned_data = leetcode_graphql_api()
    data = {
        # 'html': mark_safe(html),
        'completed_percentage':completed_percentage,
        'weather_cleaned_data' :weather_cleaned_data,
        'leetcode_cleaned_data' :leetcode_cleaned_data,
    }

    return Response(data)


def x_post():
    url = "https://publish.twitter.com/oembed?url=https://x.com/RichardsRobin_R/status/1343813927465971712&&theme=dark&&hide_media=true&&hide_thread=true"
    x_json = fetch_json_data(url)
    html = x_json["html"]
    return html



def fetch_json_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        # Handle errors appropriately
        return None

def year_percentage():
    current_date = date.today()
    year = current_date.year
    total_days = 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365
    days_passed = (current_date - date(year, 1, 1)).days + 1  # +1 to include today
    percentage = days_passed / total_days * 100
    return round(percentage)  # Rounded to no decimal places

def weather():
    # https: // api.openweathermap.org / data / 2.5 / weather?q = mysuru & appid = e853cd137996e5a3c2a1cad355747abd
    api_key = "e853cd137996e5a3c2a1cad355747abd"
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    city_name = "mysuru"

    complete_url = base_url + "?q=" + city_name + "&appid=" + api_key

    # Fri , April 04
    response = requests.get(complete_url)
    weather_json = response.json()
    current_date = date.today().day
    current_month = get_month()
    current_weekday = get_weekday()

    print(f"{current_weekday}, {current_month} {current_date}")

    if weather_json["cod"] != "404":
        weather_main_data = weather_json["main"]
        temperature = int(weather_main_data["temp"] - 273.15)
        pressure = weather_main_data["pressure"]
        humidity = weather_main_data["humidity"]
        weather_data = weather_json["weather"]
        weather_description = weather_data[0]["description"]
        location_name = weather_json["name"]

        weather_cleaned_data = {
            "temperature" : temperature,
            "pressure" : pressure,
            "humidity" : humidity,
            "weather_description" : str(weather_description).capitalize(),
            "location_name" : location_name,
            "date" : f"{current_weekday}, {current_month} {current_date}"
        }

        return weather_cleaned_data

        print(" Temperature (in kelvin unit) = " +
              str(temperature) +
              "\n atmospheric pressure (in hPa unit) = " +
              str(pressure) +
              "\n humidity (in percentage) = " +
              str(humidity) +
              "\n description = " +
              str(weather_description))

    else:
        weather_cleaned_data = {}
        return weather_cleaned_data

def get_weekday():
    weekdays = ["Mon","Tue","Wed","Thur","Fri","Sat","Sun"]
    return weekdays[date.today().weekday()]

def get_month():
    month = ["Jan","Feb","March","April","May","June","July","Aug","Sept","Oct","Nov","Dec"]
    return month[date.today().month]



def leetcode_graphql_api():
    url = "https://leetcode.com/graphql"

    query = """
    query userPublicProfileAndRanking($username: String!) {
      matchedUser(username: $username) {
        contestBadge {
          name
          expired
          hoverText
          icon
        }
        username
        githubUrl
        twitterUrl
        linkedinUrl
        profile {
          ranking
          userAvatar
          realName
          aboutMe
          school
          websites
          countryName
          company
          jobTitle
          skillTags
          postViewCount
          postViewCountDiff
          reputation
          reputationDiff
          solutionCount
          solutionCountDiff
          categoryDiscussCount
          categoryDiscussCountDiff
          certificationLevel
        }
        
    tagProblemCounts {
      advanced {
        tagName
        tagSlug
        problemsSolved
      }
      intermediate {
        tagName
        tagSlug
        problemsSolved
      }
      fundamental {
        tagName
        tagSlug
        problemsSolved
      }
    }
      }

      userContestRanking(username: $username) {
        attendedContestsCount
        rating
        globalRanking
        totalParticipants
        topPercentage
        badge {
          name
        }
      }

      
    }
    """

    query_two = """
    query getUserProfile($username: String!) {
    allQuestionsCount {
      difficulty
      count
    }
    matchedUser(username: $username) {
      contributions {
        points
      }
      profile {
        reputation
        ranking
      }
    }
    recentSubmissionList(username: $username) {
      title
      titleSlug
      timestamp
      statusDisplay
      lang
      __typename
    }
    matchedUserStats: matchedUser(username: $username) {
      submitStats: submitStatsGlobal {
        acSubmissionNum {
          difficulty
          count
          submissions
          __typename
        }
        totalSubmissionNum {
          difficulty
          count
          submissions
          __typename
        }
        __typename
      }
    }
  }
    
    """

    variables = {"username": "richardsrobinr"}

    response = requests.post(url=url, json={"query": query_two, "variables": variables})
    leetcode_cleaned_data = {}
    # print("response status code: ", response.status_code)
    if response.status_code == 200:
        # print("response : ", response.content)
        leetcode_json_data = response.json()

        leetcode_cleaned_data["all_count"] = leetcode_json_data["data"]["allQuestionsCount"][0]["count"] # total count
        leetcode_cleaned_data["easy_count"] = leetcode_json_data["data"]["allQuestionsCount"][1]["count"]
        leetcode_cleaned_data["medium_count"] = leetcode_json_data["data"]["allQuestionsCount"][2]["count"]
        leetcode_cleaned_data["hard_count"] = leetcode_json_data["data"]["allQuestionsCount"][3]["count"]
        leetcode_cleaned_data["all_completed_count"] = leetcode_json_data["data"]["matchedUserStats"]["submitStats"]["acSubmissionNum"][0]["count"]
        leetcode_cleaned_data["easy_completed_count"] = leetcode_json_data["data"]["matchedUserStats"]["submitStats"]["acSubmissionNum"][1]["count"]
        leetcode_cleaned_data["medium_completed_count"] = leetcode_json_data["data"]["matchedUserStats"]["submitStats"]["acSubmissionNum"][2]["count"]
        leetcode_cleaned_data["hard_completed_count"] = leetcode_json_data["data"]["matchedUserStats"]["submitStats"]["acSubmissionNum"][3]["count"]
        return leetcode_cleaned_data
    else:
        return leetcode_cleaned_data