function calculateReversePolish(data)
{
    // Initialize the stack
    let finalValue = 0
    let stack = [];
    const character = ["+","-","*","/"]
    const arrayValue = data.map((element,index)=> {
        if(!character.includes(element)){
            stack.push(parseInt(element));
        }
        else {
            let pop2 = parseInt(stack.pop());
            let pop1 = parseInt(stack.pop());
            if (element == "+")
                stack.push(pop1 + pop2);
            else if (element == "*")
                stack.push(pop1 * pop2);
            else if (element == "-")
                stack.push(pop1 - pop2);
            else
                stack.push(parseInt(pop1 / pop2));
        }
        return parseInt(stack[stack.length-1]);
    })
    return (arrayValue.pop())  
    
    // return finalValue
    
}
 
    let tokensA = [ "4","13","5","/","+"];
    let tokensB = ["4","2","+","5","*"]
 
    console.log(calculateReversePolish(tokensA))
    console.log(calculateReversePolish(tokensB))
