
var maxProductsSubarray = function(numArray) 
{
    var max=-10,product=1,maxInverse = -10; productInverse = 1;
    for(var i=0;i<numArray.length;i++)
    {
        

        product*=numArray[i];
        max=Math.max(max,product);
        product=(product==0?1:product);
        
        productInverse*=numArray[numArray.length-1-i];
        maxInverse=Math.max(maxInverse,productInverse);
        productInverse=(productInverse==0?1:productInverse);
    }    
    return Math.max(max, maxInverse);
};
function max(a,b)
{
    if(a>b)
        return a;
    else
        return b;
};

var maxProduct = function(nums) 
{
    var max1=-100,max2=-100,prod1=1,prod2=1,s=nums.length;
    for(var i=0;i<nums.length;i++)
    {
        //traversing from start to end and keeping the record for maximum current_product(pro1) we get till now
        prod1*=nums[i];
        max1=max(max1,prod1);//storing the maximum of current_product and max1 in max1;
        prod1=(prod1==0?1:prod1);// if we get 0 at any moment, we update the current_product(pro1) by 1.

        //traversing from end to start and keeping the record for maximum current_product(pro2) we get till now
        prod2*=nums[s-1-i];
        max2=max(max2,prod2);
        prod2=(prod2==0?1:prod2);// if we get 0 at any moment, we update the current_product(pro2) by 1.     
    }    
    return max(max1,max2);
};
var maxProduct2 = function(nums) {

    let result = nums[0]
    let currMax = nums[0]
    let currMin = nums[0]

    for (let i=1; i<nums.length; i++) {
        let localMax = Math.max(currMax * nums[i], nums[i], currMin * nums[i])
        let localMin = Math.min(currMax * nums[i], nums[i], currMin * nums[i])

        currMax = Math.max(localMax, localMin)
        currMin = Math.min(localMax, localMin)

        result = Math.max(result, currMax)


    }

    return result


  
};
console.log(maxProductsSubarray([-2,-1,0,1,2,3,4,8,5]))
console.log(maxProductsSubarray([-1,0,1]))
console.log(maxProduct([-1,0,1]))
console.log(maxProduct2([-1,0,1]))

console.log(maxProductsSubarray([-2,-3,-4,0,-1,-2,-4]))
