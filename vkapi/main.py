import os

import requests

DEBUG = True

class VKApi:
    __response = None
    def __init__(self, id_or_url: str, vk_token: str) -> None:
        self.__VKTKN = vk_token
        self.user_id = self.solve_user(id_or_url)


    def solve_user(self, id_or_url: str) -> str:
        user_info = requests.get("https://api.vk.com/method/users.get", params={
            "access_token": self.__VKTKN,
            "v": "8.131",
            "user_ids": id_or_url,
            "name_case": "gen"
        })
        user_id = user_info.json()["response"][0]["id"]
        self.__user_info = user_info.json()["response"][0]
        return user_id

    def friends_get(self) -> None:
        self.__response = requests.get("https://api.vk.com/method/friends.get", params={
            "access_token": self.__VKTKN,
            "v": "8.131",
            "user_id": self.user_id,
            "fields": "city",
            "order": "name"
        })

    def print_friends(self) -> None:
        if self.__response:
            print(f"\nДрузья {self.__user_info['first_name']} {self.__user_info['last_name']}:  \n")
            counter = 1
            for i in self.__response.json()["response"]["items"]:
                print(f'{counter})\t{i["first_name"]} {i["last_name"]} - id: {i["id"]}')
                counter += 1
        else:
            self.friends_get()
            self.print_friends()


def main():
    vktoken = os.environ.get("VKTKN")
    name = input("input user_id or short_url: ")

    api = VKApi(name, vktoken)

    api.print_friends()

    # vk.com/dev/users.get
    # my id 268734930
    # my shrturl dmitriy_shilnikov

if __name__ == '__main__':
    main()