//: Playground - noun: a place where people can play

import UIKit

var str = "Hello, playground"

var serie = 0...100

for num in serie
{
 switch num
    {
        case 30...40:
            print((num), "Viva Swift")
        default:
            if num % 5 == 0
            {
                print( (num), "Bingo")
            }else if num % 2 == 0
            {
                print((num), "Par")
            }else if num % 2 != 0
            {
                print((num), "Impar")
            }
    }
}