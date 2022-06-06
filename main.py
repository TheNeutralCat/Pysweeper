########################## IMPORTS ##########################
from objects import Settings, Game, Cursor, Clear, Dialog
import data
########################## IMPORTS ##########################

gameSettings = Settings()
pySweeper = Game(gameSettings)
dialog = Dialog(gameSettings)


while True:
  dialog.new(
    {
      "header": "PYSWEEPER v0.1",
      "padding": 2,
      "options": [
        {
          "name": "START",
          "func": lambda: pySweeper.newGame(width=24,height=12,difficulty=1) # min width is 15
        },
        {
          "name": "OPTIONS",
          "submenu": {
            "header": "OPTIONS",
            "message": "This feature is in development.",
            "weak": True,
            "options": [
              {
                "name": "OK",
                "exit": True
              }
            ]
          }
        },
        {
          "name": "ACHIEVEMENTS",
          "submenu": {
            "header": "ACHIEVEMENTS",
            "message": "This feature is planned for a future version of the game.",
            "weak": True,
            "options": [
              {
                "name": "OK",
                "exit": True
              }
            ]
          }
        },
        {
          "name": "INFO",
          "submenu": {
            "header": "INFO",
            "weak": True,
            "padding": 2,
            "options": [
              {
                "name": "HOW TO PLAY",
                "submenu": {
                  "header": "MINES",
                  "message": ["Your goal is to flag all the mines on the grid without setting any off.","You can mark tiles with the x key.","You can reveal tiles with the spacebar, but revealing a mine will kill you."],
                  "weak": True,
                  "options": [
                    {
                      "name": "<BACK",
                      "exit": True
                    },
                    {
                      "name": "NEXT>",
                      "submenu": {
                        "header": "INDICATORS",
                        "message": ["Some tiles will have numbers on them.","Number tiles display how many mines there are in the surrounding 8 tiles.","With these indicators, you can use process of elimination to flag all the mines."],
                        "weak": True,
                        "options": [
                          {
                            "name": "<BACK",
                            "exit": True
                          },
                          {
                            "name": "NEXT>",
                            "submenu": {
                              "header": "WIN",
                              "message": "When every mine has been flagged, you win!",
                              "weak": True,
                              "options": [
                                {
                                  "name": "<BACK",
                                  "exit": True
                                }
                              ]
                            }
                          }
                        ]
                      }
                    }
                  ]
                }
              },
              {
                "name": "CONTROLS",
                "submenu": {
                  "header": "CONTROLS",
                  "message": ["Flag tile: [x]","Reveal tile: [Space] or [Enter]","Redraw board: [Tab]","Exit to menu: [Esc]"],
                  "weak": True,
                  "options": [
                    {
                      "name": "OK",
                      "exit": True,
                    }
                  ]
                }
              },
              {
                "name": "STATS",
                "submenu": {
                  "header": "STATS",
                  "message": "Sorry, haven't implemented this yet either.",
                  "weak": True,
                  "options": [
                    {
                      "name": "OK",
                      "exit": True
                    }
                  ]
                }
              },
              {
                "name": "BACK",
                "exit": True
              }
            ]
          }
        }
      ]
    }
  )